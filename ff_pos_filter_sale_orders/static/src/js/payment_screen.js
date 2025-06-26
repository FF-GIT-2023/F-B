/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
patch(PaymentScreen.prototype, {
    async _finalizeValidation() {
        var order = this.pos.get_order();
        var is_sale_order = order.selected_orderline.sale_order_line_id;
        if(is_sale_order){
            order.to_invoice = true;
        }
        this.currentOrder.finalized = true;
        this.pos.showScreen(this.nextScreen);
        await super._finalizeValidation(...arguments);
    }
});
