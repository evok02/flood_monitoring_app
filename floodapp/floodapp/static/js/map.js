    const map = L.map('map').setView([47.5162, 14.5501], 7); // Austria map center

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

// Function to show stations on the map
function showStations(stationsData) {
    console.log('Show Stations button clicked'); // Debugging: Check if function is called
    console.log(stationsData); // Debugging: Check if data is available
    stationsData.forEach(station => {
        const marker = L.circleMarker([station.y, station.x], {
            radius: 8,
            fillColor: 'blue',
            color: '#000',
            weight: 1,
            fillOpacity: 0.8
        }).addTo(map);

        marker.bindPopup(`<b>Station ID: ${station.hzbnr01}</b>`);

        marker.on('mouseover', function (e) {
            this.openPopup();
        });

        marker.on('mouseout', function (e) {
            this.closePopup();
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const stationsDataElement = document.getElementById('stations-data');
    if (!stationsDataElement) {
        console.error('stations-data element not found in DOM');
        return;
    }

    let stationsData;
    try {
        stationsData = JSON.parse(stationsDataElement.textContent);
        console.log('Stations Data:', stationsData); // Debugging: Ensure data is valid
    } catch (error) {
        console.error('Failed to parse stations data:', error.message);
        return;
    }

    // Attach button event listener
    document.getElementById('show-stations').addEventListener('click', () => {
        console.log('Show Stations button clicked');
        showStations(stationsData); // Call the function with the data
    });
});

