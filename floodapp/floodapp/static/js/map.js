const map = L.map('map').setView([47.5162, 14.5501], 7); // Austria map center

// Use a standard tile layer for Austria
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

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
    console.log('Show Stations function called'); // Debugging: Check if function is called
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
    const showStationsButton = document.getElementById('show-stations');
    if (!showStationsButton) {
        console.error('show-stations button not found in DOM');
        return;
    }
    showStationsButton.addEventListener('click', () => {
        console.log('Show Stations button clicked');
        showStations(stationsData); // Call the function with the data
    });
});
// Regions and Markers
const regions = {
    vienna: { lat: 48.2082, lon: 16.3738, water_level: 2.3, risk: 'low' },
    graz: { lat: 47.0707, lon: 15.4395, water_level: 3.8, risk: 'medium' },
    salzburg: { lat: 47.8095, lon: 13.055, water_level: 5.2, risk: 'high' }
};

Object.keys(regions).forEach((regionKey, index) => {
    const region = regions[regionKey];
    const color = region.risk === 'high' ? 'red' : region.risk === 'medium' ? 'orange' : 'green';

    const marker = L.circleMarker([region.lat, region.lon], {
        radius: 8,
        fillColor: color,
        color: '#000',
        weight: 1,
        fillOpacity: 0.8
    }).addTo(map);

    marker.bindPopup(`<b>${regionKey.toUpperCase()}</b><br>Water Level: ${region.water_level} m<br>Risk: ${region.risk}`);

    // Add click listener to fetch historical data
    marker.on('click', () => {
        fetchWaterLevelHistory(index + 1); // We assume region ID is index + 1???
    });
});

// Dropdown Filter
document.getElementById('region-filter').addEventListener('change', function (e) {
    const selectedRegion = e.target.value;
    map.setView(
        selectedRegion === 'all' ? [47.5162, 14.5501] : [regions[selectedRegion].lat, regions[selectedRegion].lon],
        selectedRegion === 'all' ? 7 : 12
    );
});

// Display water level history
// URL to the backend history API
function getHistoryAPI(regionId) {
    return `/map/history/${regionId}/`;
}

// Fetch and display historical data for a region
function fetchWaterLevelHistory(regionId) {
    fetch(getHistoryAPI(regionId))
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Format historical data
                const history = data.data.map(entry => `
                    <div>
                        <p><strong>Water Level:</strong> ${entry.water_level} m</p>
                        <p><strong>Risk Level:</strong> ${entry.risk_level}</p>
                        <p><strong>Timestamp:</strong> ${entry.timestamp}</p>
                    </div>
                    <hr/>
                `).join('');

                alert(`Historical Data:\n\n${history}`);
            } else {
                alert(`Error getting data: ${data.error}`);
            }
        })
        .catch(error => {
            console.error("Error getting historical data:", error);
            alert("An error occurred while fetching data.");
        });
}

const standingWaterWfsUrl = 'https://haleconnect.com/ows/services/org.709.39dea908-344d-459e-b79b-838fd5a5c03c_wfs';

const standingWaterGeoJsonUrl = `${standingWaterWfsUrl}?service=WFS&version=2.0.0&request=GetFeature&typeName=hy-p:StandingWater&outputFormat=application/json`;

// Add StandingWater layer
fetch(standingWaterGeoJsonUrl)
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: {
                color: 'blue',
                weight: 2,
                fillColor: 'rgba(0, 0, 255, 0.5)',
                fillOpacity: 1
            }
        }).addTo(map);
    })



