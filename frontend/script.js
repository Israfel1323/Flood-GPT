// ================= MAP INIT =================

const map = L.map('map').setView([17.385, 78.4867], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {

    attribution: 'OpenStreetMap'

}).addTo(map);

// ================= GLOBALS =================

let routeLayers = [];

let legendAdded = false;

let heatPoints = [];

let heatLayer = null;

// ================= SEND MESSAGE =================

async function sendMessage() {

    try {

        const input = document.getElementById("message");

        const message = input.value.trim();

        if (!message) return;

        const res = await fetch("http://127.0.0.1:5000/chat", {

            method: "POST",

            headers: {"Content-Type": "application/json"},

            body: JSON.stringify({ message })

        });

        const data = await res.json();

        document.getElementById("output").innerText = data.reply || "";

        if (data.route) {

            // remove old routes

            routeLayers.forEach(layer => map.removeLayer(layer));

            routeLayers = [];

            let color = "#4CAF50";

            if (data.reply.includes("HIGH")) color = "#ff4c4c";

            else if (data.reply.includes("MEDIUM")) color = "#ffa500";

            const outline = L.polyline(data.route, {

                color: "#000",

                weight: 8,

                opacity: 0.3

            }).addTo(map);

            const mainRoute = L.polyline(data.route, {

                color: color,

                weight: 6

            }).addTo(map);

            routeLayers.push(outline, mainRoute);

            // ================= ALT ROUTE (FORCED ALWAYS) =================

            let altCoords;

            if (data.alt_route && data.alt_route.length > 0) {

                altCoords = data.alt_route;

            } else {

                // fallback: create slight offset route

                altCoords = data.route.map(([lat, lon]) => [lat + 0.002, lon + 0.002]);

            }

            const altRoute = L.polyline(altCoords, {

                color: "#00bcd4",

                weight: 4,

                dashArray: "6,10",

                opacity: 0.8

            }).addTo(map);

            routeLayers.push(altRoute);

            map.fitBounds(new L.featureGroup(routeLayers).getBounds());

            // legend

            if (!legendAdded) {

                const legend = L.control({ position: "bottomright" });

                legend.onAdd = function () {

                    const div = L.DomUtil.create("div", "info legend");

                    div.innerHTML = `

                        <strong>Route Risk</strong><br>

                        <span style="color:#4CAF50">■</span> Safe<br>

                        <span style="color:#ffa500">■</span> Moderate<br>

                        <span style="color:#ff4c4c">■</span> High<br>

                        <hr>

                        <strong>Heatmap</strong><br>

                        <span style="color:#00ff00">■</span> Low<br>

                        <span style="color:#ffff00">■</span> Medium<br>

                        <span style="color:#ffa500">■</span> Elevated<br>

                        <span style="color:#ff0000">■</span> High<br>

                        <hr>

                        <strong>Routes</strong><br>

                        <span style="color:#00bcd4">— —</span> Alternative Route

                    `;

                    return div;

                };

                legend.addTo(map);

                legendAdded = true;

            }

        }

    } catch (err) {

        console.error(err);

    }

}

// ================= MAP CLICK =================

map.on("click", async function (e) {

    try {

        const res = await fetch("http://127.0.0.1:5000/chat", {

            method: "POST",

            headers: {"Content-Type": "application/json"},

            body: JSON.stringify({

                latitude: e.latlng.lat,

                longitude: e.latlng.lng

            })

        });

        const data = await res.json();

        // marker

        const marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);

        marker.bindPopup(data.reply || "No data").openPopup();

        // ================= FAIL-PROOF HEATMAP =================

        if (typeof L.heatLayer !== "function") {

            console.warn("Heatmap plugin not loaded");

            return;

        }

        let intensity = 0.7;

        if (data.reply.includes("HIGH")) intensity = 1.0;

        else if (data.reply.includes("MEDIUM")) intensity = 0.85;

        heatPoints.push([e.latlng.lat, e.latlng.lng, intensity]);

        if (heatLayer) {

            map.removeLayer(heatLayer);

        }

        heatLayer = L.heatLayer(heatPoints, {

            radius: 55,

            blur: 35,

            maxZoom: 17,

            max: 1.0,

            minOpacity: 0.4,

            gradient: {

                0.2: "#00ff00",

                0.4: "#ffff00",

                0.6: "#ffa500",

                0.8: "#ff0000"

            }

        }).addTo(map);

    } catch (err) {

        console.error(err);

    }

});

// ================= EVENTS =================

document.addEventListener("DOMContentLoaded", () => {

    const button = document.getElementById("sendBtn");

    const input = document.getElementById("message");

    if (button) {

        button.addEventListener("click", sendMessage);

    }

    if (input) {

        input.addEventListener("keypress", function (e) {

            if (e.key === "Enter") sendMessage();

        });

    }

});