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

// Tracks whether the report mode is active
let isReportMode = false;
// Tracks the currently active marker during report mode
let activeMarker = null;

// Add a button to toggle report mode
const reportButton = L.control({ position: 'topright' });
reportButton.onAdd = function () {
    const button = L.DomUtil.create('button', 'report-button');
    button.innerHTML = 'Start Report';
    button.onclick = function () {
        isReportMode = !isReportMode;
        button.innerHTML = isReportMode ? 'Stop Report' : 'Start Report';
        if (!isReportMode && activeMarker) {
            map.removeLayer(activeMarker);
            activeMarker = null;
        }
    };
    return button;
};
reportButton.addTo(map);


// Handles clicks on the map to add a new marker in report mode
map.on('click', function (e) {
    if (!isReportMode) return; // Only proceed if in report mode

    const latitude = e.latlng.lat; // Get latitude from the click event
    const longitude = e.latlng.lng; // Get longitude from the click event

    if (activeMarker) {
        map.removeLayer(activeMarker); // Remove the previous marker if it exists
    }

    // Add a new marker at the clicked location
    activeMarker = L.circleMarker([latitude, longitude], {
        radius: 8,
        fillColor: 'blue', // Initial marker color
        color: '#000',
        weight: 1,
        fillOpacity: 0.8
    }).addTo(map);

    // Create a popup form for reporting the emergency
    const popupContent = `
        <div>
            <b>Report Emergency</b><br>
            <label>Description:</label><br>
            <textarea id="description" rows="2"></textarea><br>
            <label>Urgency Level:</label><br>
            <select id="urgency">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
            </select><br><br>
            <button id="submit-report">Submit</button>
        </div>
    `;

    activeMarker.bindPopup(popupContent).openPopup(); // Bind the popup to the marker

    // Add an event listener to the submit button
    document.getElementById('submit-report').addEventListener('click', function () {
        const description = document.getElementById('description').value; // Get the description
        const urgency = document.getElementById('urgency').value; // Get the urgency level

        // DEBUGGING
        console.log("Submitting report...");
        console.log("Description:", description);
        console.log("Urgency:", urgency);
        console.log("Latitude:", latitude, "Longitude:", longitude);

        // Validate user inputs
        if (!description || !['low', 'medium', 'high'].includes(urgency)) {
            alert('Please provide valid inputs.'); // Notify the user about invalid inputs
            return;
        }

        // Determine the marker color based on urgency level
        const color = urgency === 'high' ? 'red' :
                      urgency === 'medium' ? 'orange' : 'green';

        // Update the marker's color based on urgency
        activeMarker.setStyle({ fillColor: color });

        fetch('/map/report-emergency/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Include CSRF token
    },
    body: JSON.stringify({
        description: description,
        urgency_level: urgency,
        latitude: latitude, // Pass latitude
        longitude: longitude // Pass longitude
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('Report submitted successfully!'); // Notify the user of success

        // Update the popup content with the submitted report details
        activeMarker.bindPopup(`
            <b>Description:</b> ${description}<br>
            <b>Urgency:</b> ${urgency}
        `);

        // Close the popup after successful submission
        activeMarker.closePopup();

        // Reset report mode but keep the marker on the map
        isReportMode = false;
        document.querySelector('.report-button').innerHTML = 'Start Report';

        activeMarker = null; // Clear the reference, but the marker remains on the map
    } else {
        throw new Error(data.error || 'Unknown error occurred');
    }
})
.catch(error => {
    console.error('Error submitting the report:', error); // Log the error for debugging
    alert('Failed to submit the report.'); // Notify the user of failure

    // Keep the marker on the map for retry
});
    });
});

// Fetch existing emergency reports from the backend
fetch('/map/api/emergency-reports')
    .then(response => response.json())
    .then(data => {
        // DEBUGGING:
        console.log("Fetched emergency reports:", data);

        data.forEach(report => {
            if (report.latitude && report.longitude) {
                const color = report.urgency_level === 'high' ? 'red' :
                              report.urgency_level === 'medium' ? 'orange' : 'green';

                const marker = L.circleMarker([report.latitude, report.longitude], {
                    radius: 8,
                    fillColor: color,
                    color: '#000',
                    weight: 1,
                    fillOpacity: 0.8
                }).addTo(map);

                marker.bindPopup(`
                    <b>Description:</b> ${report.description}<br>
                    <b>Urgency:</b> ${report.urgency_level}<br>
                    <b>Timestamp:</b> ${report.timestamp}
                `);
            } else {
                console.error("Invalid report data:", report);
            }
        });
    })
    .catch(error => {
        console.error('Error fetching emergency reports:', error);
    });



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