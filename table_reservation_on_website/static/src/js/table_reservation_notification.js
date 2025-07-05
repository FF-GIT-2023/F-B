/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { onMounted, onWillUnmount } from "@odoo/owl";

let audioUnlocked = localStorage.getItem("pos_audio_unlocked") === "true";
let alertSound = null;

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        const rpc = useService("rpc");
        const orm = useService("orm");
        const pos = usePos();

        const alertSoundURL = '/table_reservation_on_website/static/src/audio/level-up.mp3';
        let lastOrderCount = null;
        let intervalId = null;

        const showEnableSoundPrompt = () => {
            const prompt = document.createElement("div");
            prompt.className = "pos-enable-sound-prompt";
            prompt.innerHTML = `<div class="pos-prompt-content">Click anywhere to enable sound alerts!</div>`;

            Object.assign(prompt.style, {
                position: "fixed",
                top: "60px",
                right: "15px",
                background: "#2a9d8f",
                color: "white",
                padding: "10px 15px",
                borderRadius: "8px",
                zIndex: 9999,
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
                fontSize: "14px",
                cursor: "pointer",
            });

            document.body.appendChild(prompt);

            const unlockAudio = () => {
                alertSound = new Audio(alertSoundURL);
                alertSound.volume = 1.0;
                alertSound.play().then(() => {
                    audioUnlocked = true;
                    localStorage.setItem("pos_audio_unlocked", "true");
                }).catch(err => {
                    console.warn("Audio unlock failed:", err);
                });

                document.body.removeEventListener("click", unlockAudio);
                document.body.removeEventListener("touchstart", unlockAudio);

                if (prompt.parentNode) {
                    prompt.parentNode.removeChild(prompt);
                }
            };

            document.body.addEventListener("click", unlockAudio, { once: true });
            document.body.addEventListener("touchstart", unlockAudio, { once: true });
        };

        const checkUpcomingReservations = async () => {
            try {
                const result = await rpc("/pos/reservation_alert", {});
                if (result && result.alerts.length) {
                    const shown = JSON.parse(localStorage.getItem("shown_reservations") || "[]");
                    const newAlerts = result.alerts.filter(r => !shown.includes(r.sequence));

                    if (newAlerts.length) {
                        const alertLines = newAlerts.map(
                            r => `• ${r.customer} - ${r.start_time} (Reservation: ${r.sequence})`
                        ).join('<br/>');

                        const notification = document.createElement("div");
                        notification.className = "pos-custom-notification";
                        notification.innerHTML = `
                            <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                                Upcoming Table Reservation
                            </div>
                            <div style="text-align: left;">${alertLines}</div>
                        `;

                        Object.assign(notification.style, {
                            position: "fixed",
                            top: "60px",
                            right: "15px",
                            maxWidth: "320px",
                            background: "#2a9d8f",
                            color: "white",
                            padding: "12px 16px",
                            borderRadius: "12px",
                            zIndex: 9999,
                            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
                            fontSize: "14px",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                        });

                        document.body.appendChild(notification);

                        setTimeout(() => {
                            if (notification.parentNode) {
                                notification.parentNode.removeChild(notification);
                            }
                        }, 10000);

                        if (audioUnlocked && alertSound) {
                            alertSound.currentTime = 0;
                            await alertSound.play();
                        }

                        const updated = [...shown, ...newAlerts.map(r => r.sequence)];
                        localStorage.setItem("shown_reservations", JSON.stringify(updated));
                    }
                }
            } catch (error) {
                console.error("Reservation alert fetch failed", error);
            }
        };

        onMounted(async () => {
            if (!audioUnlocked) {
                showEnableSoundPrompt();
            } else {
                alertSound = new Audio(alertSoundURL);
                alertSound.volume = 1.0;
            }

            const companyId = pos.company.id;

            lastOrderCount = await orm.call("table.reservation", "search_count", [[
                ["company_id", "=", companyId],
            ]]);

            intervalId = setInterval(async () => {
                const currentOrderCount = await orm.call("table.reservation", "search_count", [[
                    ["company_id", "=", companyId],
                ]]);

                if (currentOrderCount > lastOrderCount) {
                    lastOrderCount = currentOrderCount;

                    if (audioUnlocked && alertSound) {
                        try {
                            alertSound.currentTime = 0;
                            await alertSound.play();
                        } catch (err) {
                            console.warn("Failed to play sound:", err);
                        }
                    }

                    const notif = document.createElement("div");
                    notif.innerHTML = `<div style="font-weight:bold;font-size:16px;margin-bottom:6px;">New table reservation received!</div>`;
                    Object.assign(notif.style, {
                        position: "fixed",
                        top: "60px",
                        right: "15px",
                        maxWidth: "300px",
                        background: "#2a9d8f",
                        color: "white",
                        padding: "12px 16px",
                        borderRadius: "12px",
                        zIndex: 9999,
                        boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
                        fontSize: "14px",
                    });
                    document.body.appendChild(notif);
                    setTimeout(() => {
                        notif.remove();
                    }, 10000);
                }

                await checkUpcomingReservations();
            }, 10000);
        });

        onWillUnmount(() => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });
    },
});
