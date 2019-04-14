'use strict';

function initVisible() {
    $("input[name='level-setting']").each(function() {
        if (this.checked) {
            $('.' + this.value + '-visible').show();
        } else {
            $('.' + this.value + '-visible').hide();
        }
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

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function getLevelCategory(level) {
    return level.charAt(0).toUpperCase();
}