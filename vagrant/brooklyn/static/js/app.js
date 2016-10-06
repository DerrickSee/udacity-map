var data = [
  {
    name: "Threes Brewing",
    address: "333 Douglass St, Brooklyn, NY 11217",
    yelpId: "threes-brewing-brooklyn"
  },
  {
    name: "Freek's Mill",
    address: "285 Nevins St, Brooklyn, NY 11217",
    yelpId: "freeks-mill-gowanus"
  },
  {
    name: "Olmsted",
    address: "659 Vanderbilt Ave, Brooklyn, NY 11238",
    yelpId: "olmsted-brooklyn"
  },
  {
    name: "Carla Hall's Southern Kitchen",
    address: "115 Columbia St, Brooklyn, NY 11201",
    yelpId: "carla-halls-southern-kitchen-brooklyn"
  },
  {
    name: "Sunken Hundred",
    address: "276 Smith St, Brooklyn, NY 11231",
    yelpId: "sunken-hundred-brooklyn"
  }
]

var id = 0;

var Place = function(data) {
  var self = this;
  id += 1;
  self.id = id;
  self.name = ko.observable(data.name);
  self.yelpId = ko.observable(data.yelpId);
  self.contentString = ko.observable('<h5 id="firstHeading" class="firstHeading">' + data.name + '</h5>');
  $.ajax({
    url: "/places/" + self.yelpId(),
    success: function(result) {
      console.log(result)
      self.contentString(self.contentString() +'<p>' + result.location.address1 + '<br/>');
      self.contentString(self.contentString() +'Yelp Rating: ' + result.rating + '<br/>');
      self.contentString(self.contentString() +'Price: ' + result.price + '</p>');
      var marker = new google.maps.Marker({
        map: map,
        position: {
          lat: result.coordinates.latitude,
          lng: result.coordinates.longitude
        }
      });
      marker.addListener('click', function(e){
        marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(function(){ marker.setAnimation(null); }, 1400);
        if (infowindow) {
            infowindow.close();
        }
        infowindow = new google.maps.InfoWindow({content: self.contentString()});
        infowindow.open(map, marker);
      });
      self.marker = marker;

    }
  }).done(function(){
    if (self.id == 5) {
      loading_screen.finish();
    }
  });
}


var infowindow = null;

function AppViewModel() {
  var self = this;

  self.places = ko.observableArray();
  data.forEach(function(element, index, array) {
    self.places.push(new Place(element));
  })

  self.animateMarker = function(place){
    place.marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(function(){ place.marker.setAnimation(null); }, 1400);
    if (infowindow) {
        infowindow.close();
    }
    infowindow = new google.maps.InfoWindow({content: place.contentString()});
    infowindow.open(map, place.marker);
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
