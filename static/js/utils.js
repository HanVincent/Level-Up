'use strict';

function request(endpoint, obj, overlay) {
    return $.ajax({
        type: "POST",
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        url: endpoint,
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify(obj),
        dataType: "json",
        success: console.info,
        beforeSend: () => { overlay.removeClass('d-none'); },
        complete: () => { overlay.addClass('d-none');; }
    });
}

function debounce (func, delay) {
    let inDebounce;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(inDebounce);
        inDebounce = setTimeout(() => func.apply(context, args), delay);
    }
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}