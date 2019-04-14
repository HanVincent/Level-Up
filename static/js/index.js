'use strict';

$(document).ready(() => {
    const contentBlock = $('#content-block');

    $('#btn-clear').click(e => {
        e.preventDefault();
        contentBlock.text('');
    });

    $('#btn-copy').click(e => {
        e.preventDefault();

        const range = document.createRange();
        range.selectNodeContents(contentBlock[0]);
        const select = window.getSelection();
        select.removeAllRanges();
        select.addRange(range);
        document.execCommand('copy');

        $(e.currentTarget).tooltip('show');
        setTimeout(() => {$(e.currentTarget).tooltip('hide')}, 1500);
    });
    
    $("input[name='level-setting']").click(function(e) {
        if (e.target.checked) {
            $('.' + e.target.value + '-visible').show();
        } else {
            $('.' + e.target.value + '-visible').hide();
        }
    });
    
    SuggestTable.init();
    GrammarTable.init();
})