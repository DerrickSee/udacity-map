var data = [
  {
    name: "Threes Brewing",
    yelpId: "threes-brewing-brooklyn",
    position: {
      lat: 40.679721,
      lng: -73.982162
    }
  },
  {
    name: "Freek's Mill",
    yelpId: "freeks-mill-gowanus",
    position: {
      lat: 40.679565,
      lng: -73.986824
    }
  },
  {
    name: "Olmsted",
    yelpId: "olmsted-brooklyn",
    position: {
      lat: 40.67713,
      lng: -73.96869
    }
  },
  {
    name: "Carla Hall's Southern Kitchen",
    yelpId: "carla-halls-southern-kitchen-brooklyn",
    position: {
      lat: 40.687792,
      lng: -74.0011473
    }
  },
  {
    name: "Sunken Hundred",
    yelpId: "sunken-hundred-brooklyn",
    position: {
      lat: 40.68254,
      lng: -73.99353
    }
  }
]

var id = 0;
var infowindow = null;

var Place = function(data) {
  var self = this;
  id += 1;
  self.id = id;
  self.name = ko.observable(data.name);
  self.position = ko.observable(data.position);
  self.yelpId = ko.observable(data.yelpId);
  self.dataRetrieved = ko.observable(false);
  self.contentString = ko.observable('');
  var marker = new google.maps.Marker({
    map: map,
    position: data.position
  });
  marker.addListener('click', function(e){
    marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(function(){ marker.setAnimation(null); }, 1400);
    if (infowindow) {
        infowindow.close();
    }
    var header = '<h5>' + self.name() + '</h5>'
    if (!self.dataRetrieved()) {
      $.ajax({
        url: "/places/" + self.yelpId(),
        success: function(result) {
          out = '<p>' + result.location.address1 + '<br/>';
          out += 'Yelp Rating: ' + result.rating + '<br/>';
          out += 'Price: ' + result.price + '</p>';
          self.contentString(out);
          self.dataRetrieved(true);
        }
      }).fail(function(){
        self.contentString('<p>Unable to load data from yelp. Try again later.</p>');
      }).always(function(){
        infowindow = new google.maps.InfoWindow({content: header + self.contentString()});
        infowindow.open(map, marker);
      });
    } else {
      infowindow = new google.maps.InfoWindow({content: header + self.contentString()});
      infowindow.open(map, marker);
    }

  });
  self.marker = marker;
}

// self.contentString = ko.observable('');
//   url: "/places/" + self.yelpId(),
//   success: function(result) {
//     console.log(result)
//     self.contentString(self.contentString() +'<p>' + result.location.address1 + '<br/>');
//     self.contentString(self.contentString() +'Yelp Rating: ' + result.rating + '<br/>');
//     self.contentString(self.contentString() +'Price: ' + result.price + '</p>');
//     var marker = new google.maps.Marker({
//       map: map,
//       position: {
//         lat: result.coordinates.latitude,
//         lng: result.coordinates.longitude
//       }
//     });
//     marker.addListener('click', function(e){
//       marker.setAnimation(google.maps.Animation.BOUNCE);
//       setTimeout(function(){ marker.setAnimation(null); }, 1400);
//       if (infowindow) {
//           infowindow.close();
//       }
//       infowindow = new google.maps.InfoWindow({content: self.contentString()});
//       infowindow.open(map, marker);
//     });
//     self.marker = marker;
//   }
// }).always(function(){
//   if (self.id == 5) {
//     loading_screen.finish();
//   }
// }).fail(function(){
//   self.contentString(self.contentString() +'<p>Unable to load data from yelp. Try again later.</p>');
// });




function AppViewModel() {
  var self = this;

  self.places = ko.observableArray();
  data.forEach(function(element, index, array) {
    self.places.push(new Place(element));
  })

  self.animateMarker = function(place){
    google.maps.event.trigger(place.marker, 'click');
  }

  //filter the items using the filter text
  self.filter = ko.observable("")
  self.filteredPlaces = ko.computed(function() {
    var filter = self.filter().toLowerCase();
    if (!filter) {
        return self.places();
    } else {
      return ko.utils.arrayFilter(self.places(), function(item) {
        return stringStartsWith(item.name().toLowerCase(), filter);
      });
    }
  }, self);
}

ko.applyBindings(new AppViewModel());
