/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SaleOrderManagementScreen } from "@pos_sale/app/order_management_screen/sale_order_management_screen/sale_order_management_screen";
import { _t } from "@web/core/l10n/translation";
import { useBus, useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Orderline } from "@point_of_sale/app/store/models";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { rpc } from "@web/core/network/rpc_service";

function getId(fieldVal) {
    return fieldVal && fieldVal[0];
}

patch(SaleOrderManagementScreen.prototype, {
     setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.pos = usePos();
    },

    async onClickSaleOrder(clickedOrder) {
        // Your custom logic here
        // For example, display a custom popup
        console.log("asdasfjafsafa");
//        this.rpc = useService("rpc");
        const { confirmed, payload: selectedOption } = await this.popup.add(SelectionPopup, {
            title: _t("What do you want to do?"),
            list: [
                { id: "0", label: _t("Confirm order"), item: "settle" },
                {
                    id: "1",
                    label: _t("Cancel Order"),
                    item: "cancelled",
                },
            ],
        });

        if (confirmed) {
            let currentPOSOrder = this.pos.get_order();
            const sale_order = await this._getSaleOrder(clickedOrder.id);
            clickedOrder.shipping_date = this.pos.config.ship_later && sale_order.shipping_date;

            const currentSaleOrigin = this._getSaleOrderOrigin(currentPOSOrder);
            const currentSaleOriginId = currentSaleOrigin && currentSaleOrigin.id;

            if (currentSaleOriginId) {
                const linkedSO = await this._getSaleOrder(currentSaleOriginId);
                if (
                    getId(linkedSO.partner_id) !== getId(sale_order.partner_id) ||
                    getId(linkedSO.partner_invoice_id) !== getId(sale_order.partner_invoice_id) ||
                    getId(linkedSO.partner_shipping_id) !== getId(sale_order.partner_shipping_id)
                ) {
                    currentPOSOrder = this.pos.add_new_order();
                    this.notification.add(_t("A new order has been created."), 4000);
                }
            }

            const order_partner = this.pos.db.get_partner_by_id(sale_order.partner_id[0]);
            if (order_partner) {
                currentPOSOrder.set_partner(order_partner);
            } else {
                try {
                    await this.pos._loadPartners([sale_order.partner_id[0]]);
                } catch {
                    const title = _t("Customer loading error");
                    const body = _t(
                        "There was a problem in loading the %s customer.",
                        sale_order.partner_id[1]
                    );
                    await this.popup.add(ErrorPopup, { title, body });
                }
                currentPOSOrder.set_partner(
                    this.pos.db.get_partner_by_id(sale_order.partner_id[0])
                );
            }
            const orderFiscalPos = sale_order.fiscal_position_id
                ? this.pos.fiscal_positions.find(
                      (position) => position.id === sale_order.fiscal_position_id[0]
                  )
                : false;
            if (orderFiscalPos) {
                currentPOSOrder.fiscal_position = orderFiscalPos;
            }
            const orderPricelist = sale_order.pricelist_id
                ? this.pos.pricelists.find(
                      (pricelist) => pricelist.id === sale_order.pricelist_id[0]
                  )
                : false;
            if (orderPricelist) {
                currentPOSOrder.set_pricelist(orderPricelist);
            }

            if (selectedOption == "settle") {
                // settle the order
                const { confirmed, payload: prepTime } = await this.popup.add(NumberPopup, {
                    title: _t("Delivery Time (minutes)"),
                    body: _t("Please enter the estimated delivery time in minutes."),
                    startingValue: 0,
                    confirmText: _t("Confirm"),
                    cancelText: _t("Cancel"),
                });

                if (!confirmed) {
                    return; // User canceled the popup
                }

                const preparationTime = parseInt(prepTime, 10);
                if (isNaN(preparationTime) || preparationTime < 0) {
                    await this.popup.add(ErrorPopup, {
                        title: _t("Invalid Input"),
                        body: _t("Please enter a valid non-negative number"),
                    });
                    return;
                }
                console.log("Sale Order",sale_order);
                const lines = sale_order.order_line;
                var mail_data = {
                    'partner': sale_order.partner_id,
                    'time': preparationTime,
                    'sale_order': sale_order,
                    'lines': lines
                }
                await this.orm.call(
                    "sale.order",
                    "send_cust_mail",
                    [mail_data],
                    {}
                );
                const product_to_add_in_pos = lines
                    .filter((line) => !this.pos.db.get_product_by_id(line.product_id[0]))
                    .map((line) => line.product_id[0]);
                if (product_to_add_in_pos.length) {
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t("Products not available in POS"),
                        body: _t(
                            "Some of the products in your Sale Order are not available in POS, do you want to import them?"
                        ),
                        confirmText: _t("Yes"),
                        cancelText: _t("No"),
                    });
                    if (confirmed) {
                        await this.pos._addProducts(product_to_add_in_pos);
                    }
                }

                /**
                 * This variable will have 3 values, `undefined | false | true`.
                 * Initially, it is `undefined`. When looping thru each sale.order.line,
                 * when a line comes with lots (`.lot_names`), we use these lot names
                 * as the pack lot of the generated pos.order.line. We ask the user
                 * if he wants to use the lots that come with the sale.order.lines to
                 * be used on the corresponding pos.order.line only once. So, once the
                 * `useLoadedLots` becomes true, it will be true for the succeeding lines,
                 * and vice versa.
                 */
                let useLoadedLots;

                for (var i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    if (!this.pos.db.get_product_by_id(line.product_id[0])) {
                        continue;
                    }

                    const line_values = {
                        pos: this.pos,
                        order: this.pos.get_order(),
                        product: this.pos.db.get_product_by_id(line.product_id[0]),
                        description: line.name,
                        price: line.price_unit,
                        tax_ids: orderFiscalPos ? undefined : line.tax_id,
                        price_manually_set: false,
                        price_type: "automatic",
                        sale_order_origin_id: clickedOrder,
                        sale_order_line_id: line,
                        customer_note: line.customer_note,
                    };
                    const new_line = new Orderline({ env: this.env }, line_values);

                    if (
                        new_line.get_product().tracking !== "none" &&
                        (this.pos.picking_type.use_create_lots ||
                            this.pos.picking_type.use_existing_lots) &&
                        line.lot_names.length > 0
                    ) {
                        const { confirmed } =
                            useLoadedLots === undefined
                                ? await this.popup.add(ConfirmPopup, {
                                      title: _t("SN/Lots Loading"),
                                      body: _t(
                                          "Do you want to load the SN/Lots linked to the Sales Order?"
                                      ),
                                      confirmText: _t("Yes"),
                                      cancelText: _t("No"),
                                  })
                                : { confirmed: useLoadedLots };
                        useLoadedLots = confirmed;
                        if (useLoadedLots) {
                            new_line.setPackLotLines({
                                modifiedPackLotLines: [],
                                newPackLotLines: (line.lot_names || []).map((name) => ({
                                    lot_name: name,
                                })),
                            });
                        }
                    }
                    new_line.setQuantityFromSOL(line);
                    new_line.set_unit_price(line.price_unit);
                    new_line.set_discount(line.discount);
                    const product = this.pos.db.get_product_by_id(line.product_id[0]);
                    const product_unit = product.get_unit();
                    if (product_unit && !product.get_unit().is_pos_groupable) {
                        let remaining_quantity = new_line.quantity;
                        while (!floatIsZero(remaining_quantity, 6)) {
                            const splitted_line = new Orderline({ env: this.env }, line_values);
                            splitted_line.set_quantity(Math.min(remaining_quantity, 1.0), true);
                            splitted_line.set_discount(line.discount);
                            this.pos.get_order().add_orderline(splitted_line);
                            remaining_quantity -= splitted_line.quantity;
                        }
                    } else {
                        this.pos.get_order().add_orderline(new_line);
                    }
                }
            } else {
                    if (selectedOption == "cancelled") {
                        await this.orm.call(
                            "sale.order",
                            "cancel_sale_order_by_id",
                            [sale_order.id],
                            {}
                        );
                        this.notification.add(_t("Sale Order has been cancelled."), 3000);
                        this.pos.closeScreen();
                    }
            }

            this.pos.closeScreen();
        }
    },
});
