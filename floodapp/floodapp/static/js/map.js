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

const regions = {
    vienna: { lat: 48.2082, lon: 16.3738, water_level: 2.3, risk: 'low' },
    graz: { lat: 47.0707, lon: 15.4395, water_level: 3.8, risk: 'medium' },
    salzburg: { lat: 47.8095, lon: 13.055, water_level: 5.2, risk: 'high' }
};

Object.keys(regions).forEach(regionKey => {
    const region = regions[regionKey];
    const color = region.risk === 'high' ? 'red' : region.risk === 'medium' ? 'orange' : 'green';

    L.circleMarker([region.lat, region.lon], {
        radius: 8,
        fillColor: color,
        color: '#000',
        weight: 1,
        fillOpacity: 0.8
    }).addTo(map)
      .bindPopup(`<b>${regionKey.toUpperCase()}</b><br>Water Level: ${region.water_level} m<br>Risk: ${region.risk}`);
});

document.getElementById('region-filter').addEventListener('change', function (e) {
    const selectedRegion = e.target.value;
    map.setView(
        selectedRegion === 'all' ? [47.5162, 14.5501] : [regions[selectedRegion].lat, regions[selectedRegion].lon],
        selectedRegion === 'all' ? 7 : 12
    );
});

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


