'use strict';

function closure() {
    const overlay = $('#overlay');

    return function (endpoint, obj) {
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
}

$(document).ready(() => {
    const request = closure();
    const contentBlock = $('#content-block');
    const showcase = $('#showcase');
    const grammarDiv = $('#main-grammar');
    const vocabDiv = $('#main-vocab');


    $('#btn-submit').click(e => {
        e.preventDefault();

        const content = contentBlock.text().trim();
        if (content) {
            request("/profiling", { 'content': content }).done(main);
        }
    });

    $('#btn-clear').click(e => {
        e.preventDefault();

        contentBlock.text("");
    });

    $('#btn-copy').click(e => {
        e.preventDefault();

        const range = document.createRange();
        range.selectNodeContents(contentBlock[0]);
        const select = window.getSelection();
        select.removeAllRanges();
        select.addRange(range);
        document.execCommand('copy');
        alert("Contents copied to clipboard.");
    });

    $('#nav-grammar-tab').on('click', function (e) {
        e.preventDefault()
        if (!window.profiles) return;

        showcase.html(showcase.text());
    });

    $('#nav-vocab-tab').on('click', function (e) {
        e.preventDefault()
        if (!window.vocabs) return;

        // change showcase text
        showcase.html(vocabs.map((vocab) => {
            return !!vocab.level ?
                `<span class="highlight px-1 ${vocab.level}" data-toggle="tooltip" data-placement="top" title="${vocab.level}">${vocab.token}</span>` : vocab.token;
        }).join(' '));
    });

    contentBlock.click(e => {
        e.preventDefault();

        if (e.target.tagName === "SPAN") {
            flow(e.target.dataset.sentenceIndex);
        }
    });

    function main(response) {
        const profiles = response.profiles;
        if (profiles.length === 0) return;

        const sentences = buildSentences(profiles);
        contentBlock.html(sentences);

        window.profiles = profiles; // NOT GOOD

        // First profile
        flow(0);
    }

    function flow(profileIndex) {
        const profile = window.profiles[profileIndex];

        // render grammar table
        renderGrammar(profile);

        // render showcase
        renderShowcase(profile);

        // render vocabulary section
        if (profile.sent) {
            request("/vocabuing", { 'sentence': profile.sent })
                .done(response => {
                    window.vocabs = response.vocabs;
                    renderVocab(response.vocabs);
                });
        }
    }

    function renderShowcase(profile) {
        showcase.text(profile.parse.join(' '));
    }

    function renderGrammar(profile) {
        const grammarTable = buildGrammarTable(profile);
        grammarDiv.html(grammarTable);

        $('.accordion > .card').hover((e) => {
            const indices = e.currentTarget.dataset.indices.split(',').map(el => parseInt(el));
            const level = e.currentTarget.dataset.level;

            const tokens = profile.parse.map((token, i) =>
                indices.includes(i) ?
                    '<span class="highlight px-1 ' + level + '">' + token + '</span>' : token
            );
            showcase.html(tokens.join(' '));
        }, (e) => {
            showcase.html(showcase.text());
        });

        $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
    }

    function renderVocab(vocabs) {
        vocabDiv.html(buildVocabTable(vocabs));

        $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
    }
})