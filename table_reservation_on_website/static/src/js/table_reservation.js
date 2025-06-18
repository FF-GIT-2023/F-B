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
                self.$el.find('#legend_boxes').show();
                self.$el.find('#info').show();
                self.$el.find('#booking_info').show();
                for (let i in data) {
                    const table = data[i];
                    const amount = table.rate != 0
                        ? `<br/><span><i class="fa fa-money"></i></span><span id="rate">${table.rate}</span>/Slot`
                        : '';

                    const isReserved = table.reserved;
                    const bgColor = isReserved ? '#c0392b' : '#27ae60';
                    const pointerStyle = isReserved ? 'not-allowed' : 'pointer';
                    const tableClass = isReserved ? 'reserved' : 'available';
                    const hoverClass = isReserved ? '' : 'hover-effect';

                    const slotInfo = isReserved && table.booked_slot
                        ? `<div style="margin-top:10px;"><i class="fa fa-clock-o"></i> ${table.booked_slot.start} - ${table.booked_slot.end}</div>`
                        : '';

                    self.$el.find('#table_container_row').append(`
                        <div id="table_${table.id}" data-id="${table.id}"
                             class="card card_table ${tableClass} ${hoverClass} col-sm-2"
                             style="
                                background-color: ${bgColor};
                                padding: 0;
                                margin: 10px;
                                height: 160px;
                                width: 200px;
                                cursor: ${pointerStyle};
                                pointer-events: ${isReserved ? 'none' : 'auto'};
                                border-radius: 15px;
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                                transition: transform 0.2s ease, box-shadow 0.2s ease;
                                color: white;
                            ">
                            <div class="card-body text-center d-flex flex-column justify-content-center align-items-center" style="padding: 10px;">
                                <b style="font-size: 18px;">${table.name}</b>
                                <div style="margin-top: 10px;">
                                    <i class="fa fa-user-o" aria-hidden="true"></i> ${table.seats}
                                </div>
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
            $table.css('background-color', '#27ae60');
        } else {
            this.selectedTables.push(tableId);
            $table.css('background-color', '#2980b9');
        }
        $('#tables_input').val(this.selectedTables.join(','));
        if (this.selectedTables.length > 0) {
            $('#table_confirm').prop('disabled', false);
        } else {
            $('#table_confirm').prop('disabled', true);
        }
        },
});
