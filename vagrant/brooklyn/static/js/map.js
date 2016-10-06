var map;

function initMap() {
  geocoder = new google.maps.Geocoder();
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 40.677183, lng: -73.982564},
    zoom: 14
  });

}
