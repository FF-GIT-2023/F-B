/** @odoo-module */

import { registry } from "@web/core/registry";

const saleOrderFetcherService = registry.category("services").get("sale_order_fetcher");
const originalStart = saleOrderFetcherService.start;

saleOrderFetcherService.start = function(env, deps) {
    const instance = originalStart.call(this, env, deps);

    const originalMethod = instance._getOrderIdsForCurrentPage;

    instance._getOrderIdsForCurrentPage = async function(limit, offset) {
        const domain = [
            ["currency_id", "=", this.pos.currency.id],
            ["state", "=", "sale"],
        ].concat(this.searchDomain || []);

        this.pos.set_synch("connecting");
        const result = await this.orm.searchRead(
            "sale.order",
            domain,
            ["name", "partner_id", "amount_total", "date_order", "state", "user_id", "amount_unpaid"],
            { offset, limit }
        );
        this.pos.set_synch("connected");
        return result;
    };

    return instance;
};
