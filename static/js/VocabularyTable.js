'use strict';

const VocabularyTable = {
    API: '/vocabulary',
    overlay: $('#overlay-vocab'),
    panel: $('#main-vocab'),
    showcase: $('#showcase'),

    init: function (sentence) {
        VocabularyTable.getVocabularies(sentence);
    },
    getVocabularies: function (sentence, url = VocabularyTable.API) {
        $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify({ sentence }),
            contentType: "application/json",
            dataType: 'json',
            beforeSend: () => { VocabularyTable.overlay.removeClass('d-none'); }
        }).done(function (response) {
            if (response.vocabs.length == 0) {
                VocabularyTable.panel.text('');
            } else {
                VocabularyTable.panel.html(VocabularyTable.render(response.vocabs));

                $('#accordionVocabs > .card').hover((e) => {
                    const index = parseInt(e.currentTarget.dataset.index);
                    const level = e.currentTarget.dataset.level;
                    const tokens = response.vocabs.map((token, i) => i == index ?
                        `<span class="highlight px-1 ${level}">${token.token}</span>` : token.token);

                    VocabularyTable.showcase.html(tokens.join(' '));
                }, (e) => {
                    VocabularyTable.showcase.html(VocabularyTable.showcase.text());
                });
            }
        }).always(function () {
            $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
            VocabularyTable.overlay.addClass('d-none');
            initVisible();
        });
    },
    render: function (vocabs) {
        const table = vocabs
            .map((token, index) => Object.assign(token, { index: index }))
            .filter(vocab => vocab.level)
            .map((vocab, i) => {

                const button = vocab.recs.length == 0 ? '' :
                    `<button class="float-right btn btn-link" type="button" data-toggle="collapse" 
                         data-target="#collapse-vocab-${i}"><i class="fas fa-plus"></i>
                 </button>`;

                const recRow = vocab.recs.length > 0 ? vocab.recs.map(rec => {
                    return `<div class="d-inline-block mr-3">
                            <span class="badge ${rec.level}">${rec.level}</span> ${rec.vocab}
                        </div>`
                }).join('') : '<div>No recommend</div>'

                return `<div class="card border-right-0 border-left-0 ${getLevelCategory(vocab.level)}-visible" 
                         data-index="${vocab.index}" data-level="${vocab.level}">
                        <div class="card-header row no-gutters align-items-center p-2" 
                             id="card-head-${i}">
                            <div class="col-1">
                                <span class="badge ${vocab.level}">
                                    ${vocab.level}
                                </span>
                            </div>
                            <div class="col-10"> ${vocab.token} </div>
                            <div class="col-1"> ${button} </div>
                        </div>

                        <div id="collapse-vocab-${i}" class="collapse" data-parent="#accordionVocabs">
                            <div class="card-body row px-2 pt-0 pb-3">
                                <div class="col-1"></div>
                                <div class="col-10">${recRow}</div>
                                <div class="col-1"></div>
                            </div>
                        </div>
                    </div>`}).join('');

        return '<div class="accordion" id="accordionVocabs">' + table + '</div>';
    },
};
