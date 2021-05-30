'use strict';

const GrammarTable = {
    API: '/profiling',
    overlay: $('#overlay-grammar'),
    panel: $('#main-grammar'),
    urlInput: $('#url-input'),
    contentBlock: $('#content-block'),
    showcase: $('#showcase'),

    init: function () {
        $('#btn-url-search').click(e => {
            e.preventDefault();

            const url = GrammarTable.urlInput.val().trim();
            if (url) { GrammarTable.getGrammar(url, 'url'); }
        });

        $('#btn-submit').click(e => {
            e.preventDefault();

            const content = GrammarTable.contentBlock[0].innerText.replace(/(\s+)|(&nbsp;)/g, " ").trim();
            if (content) { GrammarTable.getGrammar(content, 'text'); }
        });

        GrammarTable.contentBlock.click(e => {
            e.preventDefault();

            if (e.target.tagName === "SPAN") { GrammarTable.render(e.target.dataset.sentenceIndex); }
        });
    },
    getGrammar: function (content, access, url = GrammarTable.API) {
        $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify({ content, access }),
            contentType: "application/json",
            dataType: 'json',
            beforeSend: () => {
                $('#nav-grammar-tab').tab('show');
                GrammarTable.overlay.removeClass('d-none');
            }
        }).done(function (response) {
            if (response.profiles.length == 0) {
                GrammarTable.panel.text('');
            } else {
                GrammarTable.profiles = response.profiles;
                GrammarTable.contentBlock.html(GrammarTable.buildSentences(response.profiles));
                GrammarTable.render(0);
            }
        }).always(function () {
            $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
            GrammarTable.overlay.addClass('d-none');
        });
    },
    // TODO: wtf is this?
    uniq: function (matches, recs) {
        const cacheTable = {};
        const newMatches = [];
        let i = 0;
        matches.forEach((match, index) => {
            if (cacheTable.hasOwnProperty(match.rule_num)) {
                newMatches[cacheTable[match.rule_num]].indices.push(...match.indices);
                if (recs[index]) {
                    newMatches[cacheTable[match.rule_num]].rec.sentences.push(recs[index].sentence);
                }
            } else {
                if (recs[index]) {
                    Object.assign(recs[index], { sentences: [recs[index].sentence] })
                }
                newMatches.push(Object.assign(match, { rec: recs[index] }));
                cacheTable[match.rule_num] = i++;
            }
        })
        return newMatches
    },
    buildSentences: function (profiles) {
        const sentences = profiles.map((profile, i) => {
            const sentence = profile.sentence;

            return `<span id="span-${i}" class="sent hoverable" data-sentence-index="${i}">
                        ${sentence} 
                    </span>`
        });
        return sentences.join(' ');
    },
    buildGrammar: function (profile) {
        const { matches, recs } = profile;

        const table = GrammarTable.uniq(matches, recs)
            .map((match, i) => {

                const recRow = match.rec ? `<ul class="pl-4 pb-1">
                                        <li>
                                            <span class="badge ${match.rec.level}" data-toggle="tooltip" 
                                                  data-placement="top" 
                                                  title="${match.rec.category} ${match.rec.subcategory}">
                                                ${match.rec.level}
                                            </span>
                                            ${match.rec.statement} 
                                            <number></number>
                                            ${match.rec.sentences.map(sent =>
                    `<div class="px-2 py-1 mt-2 text-monospace bg-light">
                                                    <small>${sent}</small></div>`).join('')}
                                        </li>
                                    </ul>` : '<tr>No recommend</tr>'

                return `<div class="card border-right-0 border-left-0 ${getLevelCategory(match.level)}-visible ${match.category}-visible" data-indices="${match.indices.join(',')}" 
                         data-level="${match.level}">
                        <div class="card-header ${match.category} row no-gutters align-items-center p-2" 
                             id="card-head-${i}">
                            <div class="col-1">
                                <span class="badge ${match.level}" data-toggle="tooltip" data-placement="top" 
                                      title="${match.category} ${match.subcategory}">
                                    ${match.level}
                                </span>
                            </div>
                            <div class="col-10">
                                ${match.statement} 
                                <number></number>
                            </div>
                            <div class="col-1">
                            ${match.rec ? `<button class="float-right btn btn-link" type="button" 
                                                data-toggle="collapse" data-target="#collapse-get-${i}">
                                            <i class="fas fa-plus"></i>
                                        </button>` : ''}
                            </div>
                        </div>

                        <div id="collapse-get-${i}" class="collapse" data-parent="#accordionGets">
                            <div class="card-body p-2">
                                ${recRow}
                            </div>
                        </div>
                    </div>`}).join('');

        return table ? `<div class="accordion" id="accordionGets">${table}</div>` : '';
    },
    render: function (index) {
        const profile = GrammarTable.profiles[index];

        GrammarTable.showcase.text(profile.tokens.join(' '));
        GrammarTable.panel.html(GrammarTable.buildGrammar(profile));
        initVisible();

        VocabularyTable.init(profile.sentence);

        $('#accordionGets > .card').hover((e) => {
            const level = e.currentTarget.dataset.level;
            const indices = e.currentTarget.dataset.indices.split(',').map(el => parseInt(el));
            const tokens = profile.tokens.map((token, i) =>
                indices.includes(i) ?
                    '<span class="highlight px-1 ' + level + '">' + token + '</span>' : token
            );
            GrammarTable.showcase.html(tokens.join(' '));
        }, (e) => {
            GrammarTable.showcase.html(GrammarTable.showcase.text());
        });
    },
};
