$(document).keydown(function(event){
    if(event.which=="17")
        ctrlIsPressed = true;
    if(event.which=="18")
        altIsPressed = true;
    if(event.which=="91" || event.which=="93" || event.which=="224")
        cmdIsPressed = true;
});

$(document).keyup(function(){
    ctrlIsPressed = false;
    altIsPressed = false;
    cmdIsPressed = false;
});

var ctrlIsPressed = false;
var altIsPressed = false;
var cmdIsPressed = false;

// Pagination

function set_paginator_page(page) {
    document.getElementById('paginator_page').value = page;
    document.getElementById('form').submit();
}

function set_paginator_size(size) {
    document.getElementById('paginator_size').value = size;
    document.getElementById('form').submit();
}

function sort2(sort) {
    document.getElementById('sort').value = sort;
    document.getElementById('form').submit();
}

function send(action) {
    document.getElementById('action').value = action;
    document.getElementById('form').submit();
}

function send2(action) {
    send(action);
    $('#action').val('');
}

function open2(url) {
    var selection = window.getSelection();
    if (selection.toString().length === 0) {
        var previous_url = document.URL
        if (document.getElementById('form').action)
            previous_url = document.getElementById('form').action.baseURI;
        if (ctrlIsPressed || altIsPressed || cmdIsPressed)
            document.getElementById('form').target = '_blank';
        document.getElementById('action').value = '';
        document.getElementById('form').action = url;
        document.getElementById('form').submit();
        if (ctrlIsPressed || altIsPressed || cmdIsPressed)
            document.getElementById('form').target = '';
            document.getElementById('form').action = new URL(previous_url).pathname;
    }
}
function goto(url) {
    var selection = window.getSelection();
    if (selection.toString().length === 0) {
        location.href=url;
    }
}

function go_back(url) {
    document.getElementById('action').value = 'back';
    document.getElementById('form').action = url;
    document.getElementById('form').submit();
}

function printTo(route, report) {
    document.getElementById('action').value = '';
    document.getElementById('report').value = report;
    document.getElementById('form').action = route;
    document.getElementById('form').submit();
}

function clear_search() {
    document.getElementById('search').value = '';
    document.getElementById('form').submit();
}

function copy_to_clipboard(url) {

    url = url + '?copy';

    sort = document.getElementById('sort').value;
    if (sort != '')
        url = url + '&sort=' + sort

    search = document.getElementById('search').value;
    if (search != '')
        url = url + '&search=' + search

    filter_key = document.getElementById('filter_key').value;
    if (filter_key != '')
        url = url + '&filter_key=' + filter_key

    $.ajax({
        url: url,
        dataType: 'text',
        async: false,
        processData: false,
        contentType: false,
        type: 'GET',
        success: function(data) {
            navigator.clipboard.writeText(data);
        }
    });
}

function open_item(url, page) {
    document.getElementById('paginator_page').value = page;
    document.getElementById('action').value = 'open_item';
    document.getElementById('form').action = url;
    document.getElementById('form').submit();
}

// Zip and City

function setLabel(id, label) {
    var html = "";
    var words = label.split(" ");
    for (var i = 0; i < words.length; i++) {
        if (i > 0) html += " ";
        html += words[i].slice(0, 1) + "&zwj;" + words[i].slice(1);
    }
    document.getElementById(id).innerHTML = html;
}

function setZip(zip) {
    document.getElementById('zip').value = zip;
    document.getElementById('auto_zi').value = zip;
}

function setCity(city) {
    document.getElementById('city').value = city;
    document.getElementById('auto_ci').value = city;
}

function setZipAndCity(zip, city) {
    setZip(zip);
    setCity(city);
}

old_zip = null;
old_city = null;

function storeZipAndCity() {
    old_zip = document.getElementById("auto_zi").value;
    old_city = document.getElementById("auto_ci").value;
}

function resetZipAndCity() {
    reset = false;
    if (old_zip != null && document.getElementById("auto_zi").value != old_zip) {
        setZip(old_zip);
        reset = true;
    }
    if (old_city != null && document.getElementById("auto_ci").value != old_city) {
        setCity(old_city);
        reset = true;
    }
    return reset;
}

function registerZipAndCity(id) {
    document.getElementById(id).onfocus = function() {
        storeZipAndCity();
    };
    document.getElementById(id).addEventListener('keydown', function(event){
        if (event.key === "Escape") {
            if (resetZipAndCity()) {
                event.stopPropagation();
            }
        }
    });
}