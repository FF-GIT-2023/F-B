/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.table_reservation = publicWidget.Widget.extend({
    selector: '.swa_container',
    events: {
        'change #floors_rest': '_onFloorChange',
        'click .card_table.available': '_onTableClick',
    },

    selectedTables: [],

    _onFloorChange: function () {
        const self = this;
        const floors = this.$el.find("#floors_rest")[0].value;
        const date = this.$el.find("#date_booking").text().trim();
        const startTime = this.$('#start_id').val();
        const endTime = this.$('#end_id').val();

        self.selectedTables = [];

        if (floors && date && startTime && endTime) {
            jsonrpc("/restaurant/floors/tables", {
                'floors_id': floors,
                'date': date,
                'start': startTime,
                'end': endTime
            }).then(function (data) {
                self.$el.find('#table_container_row').empty();
                self.$el.find('#info').show();

                for (let i in data) {
                    const table = data[i];
                    const amount = table.rate != 0 ? `<br/><span><i class="fa fa-money"></i></span><span id="rate">${table.rate}</span>/Slot` : '';

                    const isReserved = table.reserved;
                    const bgColor = isReserved ? '#dc3545' : '#28a745';
                    const pointerStyle = isReserved ? 'not-allowed' : 'pointer';
                    const tableClass = isReserved ? 'reserved' : 'available';
                    const slotInfo = isReserved && table.booked_slot
                        ? `<div style="margin-top:10px;"><i class="fa fa-clock-o"></i>Booked on ${table.booked_slot.start} - ${table.booked_slot.end}</div>`
                        : '';

                    self.$el.find('#table_container_row').append(`
                        <div id="table_${table.id}" data-id="${table.id}" class="card card_table ${tableClass} col-sm-2"
                             style="background-color:${bgColor};padding:0;margin:10px;width:250px;cursor:${pointerStyle};">
                            <div class="card-body text-center">
                                <b>${table.name}</b><br/><br/>
                                <span><i class="fa fa-user-o" aria-hidden="true"></i> ${table.seats}</span>
                                ${amount}
                                ${slotInfo}
                            </div>
                        </div>
                    `);
                }
            });
        }
    },

    _onTableClick: function (ev) {
        const $table = $(ev.currentTarget);
        const tableId = parseInt($table.attr('data-id'));
        if (this.selectedTables.includes(tableId)) {
            this.selectedTables = this.selectedTables.filter(id => id !== tableId);
            $table.css('background-color', '#28a745');
        } else {
            this.selectedTables.push(tableId);
            $table.css('background-color', '#007bff');
        }
        $('#tables_input').val(this.selectedTables.join(','));
    },
});
