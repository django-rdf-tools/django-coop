/* main initialisation function */
var epsg_display_projection = new OpenLayers.Projection('EPSG:4326');
var epsg_projection = new OpenLayers.Projection('EPSG:900913');
var centerLonLat = new OpenLayers.LonLat(-1.679444,48.114722).transform(epsg_display_projection, epsg_projection);
var markers;

function osm_getTileURL(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
    var z = this.map.getZoom();
    var limit = Math.pow(2, z);

    if (y < 0 || y >= limit) {
        return OpenLayers.Util.getImagesLocation() + "404.png";
    } else {
        x = ((x % limit) + limit) % limit;
        return this.url + z + "/" + x + "/" + y + "." + this.type;
    }
}

function init(){
    /* set the main map */
    var options = {
        controls:[new OpenLayers.Control.Navigation(),
                  new OpenLayers.Control.PanZoomBar()],
        maxResolution: 156543.0399,
        units: 'm',
        projection: new OpenLayers.Projection('EPSG:4326'),
        theme:null
    };
    map = new OpenLayers.Map('map', options);
    map.addLayers(map_layers);
    /*for (idx in map_extra_layers){
        map.addLayer(map_extra_layers[idx]);
    }*/
    markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);

    /*
    map.events.register('click', map, hidePopUp);
    if (dynamic_categories){
        map.events.register('moveend', map, refreshMapItems);
    }*/
    map.setCenter(centerLonLat, 13);
}


var currentPopup;
var clicked = false;

function showPop(feature) {
    if (currentPopup != null) {
      currentPopup.hide();
    }
    if (feature.popup == null) {
        feature.popup = feature.createPopup();
        map.addPopup(feature.popup);
    } else {
        feature.popup.toggle();
    }
    currentPopup = feature.popup;
    /* hide on click on the cloud */
    currentPopup.groupDiv.onclick = hidePopUp;
}

var hidePopUp = function (evt) {
    if (clicked) {
        currentPopup.hide();
        clicked = false;
    }
}

var size = new OpenLayers.Size(20,34);
var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
var icon = new OpenLayers.Icon('http://www.google.com/mapfiles/marker.png', size, offset);

/* put a marker on the map */
function putMarker(lat, lon, text) {
    /* initialise a new marker with appropriate attribute for setting a marker */
    var feature = new OpenLayers.Feature(markers,
              new OpenLayers.LonLat(lon, lat).transform(epsg_display_projection,
                                                        epsg_projection),
              {icon:icon.clone()});
    /*feature.closeBox = false;*/
    feature.popupClass = OpenLayers.Class(OpenLayers.Popup.FramedCloud);
    feature.data.popupContentHTML = "<div class='cloud'>";
    feature.data.popupContentHTML += text;
    feature.data.popupContentHTML += "</div>";
    feature.data.overflow = 'hidden';
    var marker = feature.createMarker();
    /* manage markers events */
    var markerClick = function (evt) {
        if (clicked) {
            if (currentPopup == this.popup) {
                this.popup.hide();
                clicked = false;
            } else {
                currentPopup.hide();
                showPop(this);
            }
        } else {
            showPop(this);
            clicked = true;
        }
        OpenLayers.Event.stop(evt);
    };
    var markerOver = function (evt) {
        document.body.style.cursor='pointer';
        OpenLayers.Event.stop(evt);
    };
    var markerOut = function (evt) {
        document.body.style.cursor='auto';
        OpenLayers.Event.stop(evt);
    };
    marker.events.register('click', feature, markerClick);
    marker.events.register('mouseover', feature, markerOver);
    marker.events.register('mouseout', feature, markerOut);
    markers.addMarker(marker);
    return feature;
}
