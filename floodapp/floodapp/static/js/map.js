// Initialize the map
const map = L.map('map').setView([47.5162, 14.5501], 8); // Austria map center

// Use a standard tile layer for Austria
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Load GeoJSON data for Austria
fetch(austriaGeoJsonUrl)
    .then(response => response.json())
    .then(data => {
        // Add Austria GeoJSON layer with no fill
        L.geoJSON(data, {
            style: {
                color: 'none',  // Border color
                weight: 2,      // Border width
                fillColor: 'none', // No fill color for Austria
                fillOpacity: 0
            }
        }).addTo(map);

        // Create a white overlay for the rest of the world
        const worldGeoJson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]
                        ]]
                    },
                    "properties": {}
                }
            ]
        };

        // Subtract Austria from the world polygon
        const difference = turf.difference(worldGeoJson.features[0], data.features[0]);

        // Add the white overlay to the map
        L.geoJSON(difference, {
            style: {
                color: 'orange',  // Border color
                weight: 0.5,      // No border width
                fillColor: 'rgb(211,211,211)', // Fill color for the rest of the world
                fillOpacity: 0.6
            }
        }).addTo(map);
    });

// Define WMS layers
const hq30Layer = L.tileLayer.wms("https://inspire.lfrz.gv.at/000801/wms", {
    layers: "Hochwasserueberflutungsflaechen HQ30",
    version: "1.3.0",
    format: "image/png",
    transparent: true,
    attribution: "@ Umweltbundesamt",
    zIndex: 2
});

const hq100Layer = L.tileLayer.wms("https://inspire.lfrz.gv.at/000801/wms", {
    layers: "Hochwasserueberflutungsflaechen HQ100",
    version: "1.3.0",
    format: "image/png",
    transparent: true,
    attribution: "@ Umweltbundesamt",
    zIndex: 2
});

// Add checkboxes for toggling layers
const layersControlDiv = L.control({ position: 'topright' });

layersControlDiv.onAdd = function () {
    const container = L.DomUtil.create('div', 'leaflet-control-layers');
    container.innerHTML = `
        <label>
            <input type="checkbox" id="hq30-checkbox" /> HQ30 Flood Areas
        </label>
        <br />
        <label>
            <input type="checkbox" id="hq100-checkbox" /> HQ100 Flood Areas
        </label>
    `;
    L.DomEvent.disableClickPropagation(container);

    // Add event listeners for the checkboxes
    container.querySelector('#hq30-checkbox').addEventListener('change', (e) => {
        if (e.target.checked) {
            map.addLayer(hq30Layer);
        } else {
            map.removeLayer(hq30Layer);
        }
    });

    container.querySelector('#hq100-checkbox').addEventListener('change', (e) => {
        if (e.target.checked) {
            map.addLayer(hq100Layer);
        } else {
            map.removeLayer(hq100Layer);
        }
    });

    return container;
};

layersControlDiv.addTo(map);


const regions = {
    vienna: { lat: 48.2082, lon: 16.3738, water_level: 2.3, risk: 'low' },
    graz: { lat: 47.0707, lon: 15.4395, water_level: 3.8, risk: 'medium' },
    salzburg: { lat: 47.8095, lon: 13.055, water_level: 5.2, risk: 'high' },
    innsbruck: { lat: 47.2692, lon: 11.4041, water_level: 3.5, risk: 'medium' },
    klagenfurt: { lat: 46.6368, lon: 14.3122, water_level: 2.9, risk: 'low' },
    stpoelten: { lat: 48.2038, lon: 15.6267, water_level: 3.2, risk: 'medium' },
    bregenz: { lat: 47.5031, lon: 9.7471, water_level: 4.0, risk: 'medium' },
    eisenstadt: { lat: 47.8457, lon: 16.5338, water_level: 2.7, risk: 'low' },
    krems: { lat: 48.4100, lon: 15.6014, water_level: 3.0, risk: 'low' }
};

// Object.keys(regions).forEach(regionKey => {
//     const region = regions[regionKey];
//     const color = region.risk === 'high' ? 'red' : region.risk === 'medium' ? 'orange' : 'green';

//     L.circleMarker([region.lat, region.lon], {
//         radius: 8,
//         fillColor: color,
//         color: '#000',
//         weight: 1,
//         fillOpacity: 0.8
//     }).addTo(map)
//       .bindPopup(`<b>${regionKey.toUpperCase()}</b><br>Water Level: ${region.water_level} m<br>Risk: ${region.risk}`);
// });

// Add region filter control
document.getElementById('region-filter').addEventListener('change', function (e) {
    const selectedRegion = e.target.value;
    map.setView(
        selectedRegion === 'all' ? [47.5162, 14.5501] : [regions[selectedRegion].lat, regions[selectedRegion].lon],
        selectedRegion === 'all' ? 7 : 12
    );
});
