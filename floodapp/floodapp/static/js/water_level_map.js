// Fetch and display measurement stations
const map = L.map('map').setView([47.5162, 14.5501], 8); // Austria map center

// Use a standard tile layer for Austria
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch and display measurement stations
fetch('https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&service=WFS&version=2.0.0&request=GetFeature&typeName=inspire:pegelaktuell&outputFormat=application/json')
    .then(response => response.json())
    .then(data => {
        console.log('GeoJSON Data:', data); // Debug log

        L.geoJSON(data, {
            onEachFeature: (feature, layer) => {
                const properties = feature.properties;
                console.log('Feature Properties:', properties); // Debug log

                const popupContent = `
                    <strong>Measurement Station:</strong> ${properties.messstelle || 'N/A'}<br>
                    <strong>River:</strong> ${properties.gewaesser || 'N/A'}<br>
                    <strong>Flow:</strong> ${properties.wert || 'N/A'} ${properties.einheit || ''}<br>
                    <strong>Time:</strong> ${properties.zeitpunkt || 'N/A'}<br>
                    <a href="/map/historical-data/?hzbnr=${properties.hzbnr}" target="_blank">Get historical data</a>
                    <a href="${properties.internet}" target="_blank">More Info</a>
                `;
                layer.bindPopup(popupContent);
            },
            pointToLayer: (feature, latlng) => {
                const riskColor = !isNaN(parseFloat(feature.properties.wert)) && parseFloat(feature.properties.wert) > 10 ? 'red' : 'blue';
                const properties = feature.properties;
                console.log('Lat:', properties.lat, 'Lon:', properties.lon); // Debug log

                // Check if lat and lon are present and correctly formatted
                if (!properties.lat || !properties.lon) {
                    console.error('Missing lat or lon:', properties);
                    return;
                }

                // Convert lat and lon from string with comma to float with dot
                const lat = parseFloat(properties.lat.replace(',', '.'));
                const lon = parseFloat(properties.lon.replace(',', '.'));

                // Check if lat and lon are valid numbers
                if (isNaN(lat) || isNaN(lon)) {
                    console.error('Invalid lat or lon:', properties);
                    return;
                }

                console.log('Converted Lat:', lat, 'Converted Lon:', lon); // Debug log

                return L.circleMarker([lat, lon], {
                    radius: 8,
                    fillColor: riskColor,
                    color: '#000',
                    weight: 1,
                    fillOpacity: 0.8
                }).bringToFront();
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error fetching GeoJSON:', error));


// Fetch and display rivers
fetch(waterLevelGeoJsonUrl)
    .then(response => response.json())
    .then(data => {
        console.log('Rivers GeoJSON Data:', data); // Debug log

        L.geoJSON(data, {
            style: {
                color: 'blue',  // Border color
                weight: 0.5,      // Border width
                fillColor: 'blue', // Fill color for rivers
                fillOpacity: 0.5
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error fetching rivers GeoJSON:', error));

// Load GeoJSON data for Austria
fetch(austriaGeoJsonUrl)
    .then(response => response.json())
    .then(data => {
        // Add Austria GeoJSON layer with no fill
        L.geoJSON(data, {
            style: {
                color: 'none',  // Border color
                weight: 2,      // Border width
                fillColor: 'white', // No fill color for Austria
                fillOpacity: 0.7
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
                fillColor: 'gray', // Fill color for the rest of the world
                fillOpacity: 0.9
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error fetching GeoJSON:', error));




