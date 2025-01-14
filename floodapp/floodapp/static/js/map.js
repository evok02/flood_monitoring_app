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

// Tracks whether the report mode is active
let isReportMode = false;
// Tracks the currently active marker during report mode
let activeMarker = null;

// Adds a button to toggle report mode
const reportButton = L.control({ position: 'topright' });
reportButton.onAdd = function () {
    const button = L.DomUtil.create('button', 'report-button');
    button.innerHTML = 'Start Report';
    button.style.cursor = 'pointer';
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

        // Send the data to the backend
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

                // Reset the report mode
                activeMarker = null;
                isReportMode = false;
                document.querySelector('.report-button').innerHTML = 'Start Report';
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error submitting the report:', error); // Log the error for debugging
            alert('Failed to submit the report.'); // Notify the user of failure
            if (activeMarker) {
                map.removeLayer(activeMarker); // Remove the active marker on failure
                activeMarker = null;
            }
        });
    });
});
