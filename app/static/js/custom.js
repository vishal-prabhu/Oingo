let map;

function initMap(latitude, longitude) {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: latitude, lng: longitude},
        zoom: 18,
        mapTypeId: 'roadmap',
        disableDefaultUI: true,
        draggable: false,
        styles: [
            {
                "featureType": "poi.business",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            }
        ]
    });
    let marker = new google.maps.Marker({
        position: {lat: latitude, lng: longitude},
        map: map
    });
}

function initTrackingMap(pointsarray, notesarray, note_marker_url) {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: pointsarray[0].latitude, lng: pointsarray[0].longitude},
        zoom: 12,
        mapTypeId: 'roadmap',
        disableDefaultUI: true,
        styles: [
            {
                "featureType": "poi.business",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            }
        ]
    });
    let first = true;
    for (let point of pointsarray) {
        let marker = new google.maps.Marker({
            position: {lat: point.latitude, lng: point.longitude},
            map: map
        });
        if (first) {
            marker.setAnimation(google.maps.Animation.BOUNCE);
            first = false;
        }
    }

    for (let note of notesarray) {
        let marker = new google.maps.Marker({
            position: {lat: note.latitude, lng: note.longitude},
            map: map,
            icon: note_marker_url
        });

        (function (marker) {
            // add click event
            google.maps.event.addListener(marker, 'click', function () {
                infowindow = new google.maps.InfoWindow({
                    content: note.content + ' ' + '<a href=' + note.url + '>link</a>'
                });
                infowindow.open(map, marker);
            });
        })(marker);
    }

    google.maps.event.addListener(map, 'click', function (event) {
        $('#latitude')[0].value = event.latLng.lat();
        $('#longitude')[0].value = event.latLng.lng();
    });
}

function insert_tag_into_input() {
    let form_tag_input = document.getElementById('tags');
    let chip_element = document.getElementsByClassName('chips')[0];
    let instance = M.Chips.getInstance(chip_element);
    let output_string = "";
    for (let each_tag of instance.chipsData) {
        output_string = output_string.concat('$' + each_tag.tag);
    }
    form_tag_input.value = output_string;
}

function mapinput() {
    // let latitude = 40.694206, longitude = -73.986609;
    let initial_position = {lat: 40.69847032728747, lng: -73.9514422416687};
    map = new google.maps.Map(document.getElementById('map'), {
        center: initial_position,
        zoom: 10,
        mapTypeId: 'roadmap',
        disableDefaultUI: true,
        styles: [
            {
                "featureType": "poi.business",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            }
        ]
    });
    let marker = new google.maps.Marker({
        position: initial_position,
        map: map,
        draggable: true,
    });
    navigator.geolocation.getCurrentPosition(function (position) {
        let current_position = {lat: position.coords.latitude, lng: position.coords.longitude};

        marker.setPosition(current_position);
        map.setCenter(current_position);
        map.setZoom(18);

        $('#latitude')[0].value = current_position.lat;
        $('#longitude')[0].value = current_position.lng;
    }, function (error) {
        console.log(error);
    });

    google.maps.event.addListener(map, 'click', function (event) {
        marker.setPosition(event.latLng);
        // marker.position = {lat: event.latLng.lat(), lng: event.latLng.lng()};
        $('#latitude')[0].value = event.latLng.lat();
        $('#longitude')[0].value = event.latLng.lng();
    });
    google.maps.event.addListener(marker, "dragend", function (event) {
        $('#latitude')[0].value = event.latLng.lat();
        $('#longitude')[0].value = event.latLng.lng();
    });
}

function replytocomment(comment_id) {
    $('#parent_id')[0].value = comment_id;
}

function disable_location_field() {
    let label = document.getElementById('locationdiv').firstElementChild;
    label.innerHTML = 'Location Already Set';
    let input_box = document.getElementById('region_name');
    input_box.value = '';
    input_box.disabled = true;
}

function enable_location_field() {
    let label = document.getElementById('locationdiv').firstElementChild;
    label.innerHTML = 'Location';
    let input_box = document.getElementById('region_name');
    input_box.value = '';
    input_box.disabled = false;
}