var map = new L.Map("addresses-map", { center: new L.LatLng(47.628, 2.703), zoom: 5 });
var addresses_points = JSON.parse(document.getElementById("addresses-points").textContent);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
    tileSize: 512,
    zoomOffset: -1,
}).addTo(map);
var iconProduction = L.icon({
    iconUrl: document.getElementById("industry-icon-address").textContent,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [20, 0],
});
function onEachAddress(feature, layer) {
    if (feature.properties && feature.properties.text_version) {
        layer.bindPopup(feature.properties.text_version);
    }
}
function addressToLayer(geoJsonPoint, latlng) {
    if (geoJsonPoint.properties.is_production) {
        return L.marker(latlng, { icon: iconProduction });
    }
    else
        return L.marker(latlng);
}
var jsonlayer = L.geoJSON(addresses_points, { pointToLayer: addressToLayer, onEachFeature: onEachAddress }).addTo(map);
