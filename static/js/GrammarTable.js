'use strict';

const GrammarTable = {
    API: '/profiling',
    overlay: $('#overlay-grammar'),
    panel: $('#main-grammar'),
    urlInput: $('#url-input'),
    contentBlock: $('#content-block'),
    showcase: $('#showcase'),

    init: function() {
        $('#btn-url-search').click(e => {
            e.preventDefault();

            const url = GrammarTable.urlInput.val().trim();
            if (url) { GrammarTable.getGrammar(url, 'url'); }
        });

        $('#btn-submit').click(e => {
            e.preventDefault();

            const content = GrammarTable.contentBlock[0].innerText.replace(/(\s+)|(&nbsp;)/g," ").trim();
            if (content) { GrammarTable.getGrammar(content, 'text'); }
        });
        
        GrammarTable.contentBlock.click(e => {
            e.preventDefault();

            if (e.target.tagName === "SPAN") { GrammarTable.render(e.target.dataset.sentenceIndex); }
        });
    },
    getGrammar: function(content, access, url=GrammarTable.API){
        $.ajax({
          url: url,
          type: 'POST',
          data: JSON.stringify({content: content, access: access}),
          contentType: "application/json",
          dataType: 'json',
          beforeSend: () => { 
              $('#nav-grammar-tab').tab('show');
              GrammarTable.overlay.removeClass('d-none'); 
          }
        }).done(function(response) {
            if (response.profiles.length == 0) {
                GrammarTable.panel.text(''); 
            } else { 
                GrammarTable.profiles = response.profiles;
                GrammarTable.contentBlock.html(GrammarTable.buildSentences(response.profiles));
                GrammarTable.render(0);
            }
        }).always(function() {
            $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
            GrammarTable.overlay.addClass('d-none');
        });
    },
    uniq: function(gets, recs) { // want to delete
        const cacheTable = {};
        const newGets = [];
        let i = 0;
        gets.forEach((get, index) => {
            if (cacheTable.hasOwnProperty(get.no)) {
                newGets[cacheTable[get.no]].indices.push(...get.indices);
                if (recs[index]) { newGets[cacheTable[get.no]].rec.examples.push(recs[index].example); }
            } else {
                if (recs[index]) { Object.assign(recs[index], { examples: [recs[index].example] }) }
                newGets.push(Object.assign(get, {rec: recs[index]}));
                cacheTable[get.no] = i++;
            }
        })
        return newGets
    },
    buildSentences: function(profiles) {
        const sentences = profiles.map((profile, i) => {
            const sent = profile.sent;

            return `<span id="span-${i}" class="sent hoverable" data-sentence-index="${i}">
                        ${sent} 
                    </span>`
        });
        return sentences.join(' ');
    },
    buildGrammar: function(profile) {
        const { gets, recs } = profile;
        
        const table = GrammarTable.uniq(gets, recs)
        .map((get, i) => {
    
            const recRow = get.rec? `<ul class="pl-4 pb-1">
                                        <li>
                                            <span class="badge ${get.rec.level}" data-toggle="tooltip" 
                                                  data-placement="top" 
                                                  title="${get.rec.category} ${get.rec.subcategory}">
                                                ${get.rec.level}
                                            </span>
                                            ${get.rec.statement} 
                                            <number></number>
                                            ${get.rec.examples.map(ex => 
                                                `<div class="px-2 py-1 mt-2 text-monospace bg-light">
                                                    <small>${ex}</small></div>`).join('')}
                                        </li>
                                    </ul>` : '<tr>No recommend</tr>'

            return `<div class="card border-right-0 border-left-0 ${getLevelCategory(get.level)}-visible ${get.category}-visible" data-indices="${get.indices.join(',')}" 
                         data-level="${get.level}">
                        <div class="card-header ${get.category} row no-gutters align-items-center p-2" 
                             id="card-head-${i}">
                            <div class="col-1">
                                <span class="badge ${get.level}" data-toggle="tooltip" data-placement="top" 
                                      title="${get.category} ${get.subcategory}">
                                    ${get.level}
                                </span>
                            </div>
                            <div class="col-10">
                                ${get.statement} 
                                <number></number>
                            </div>
                            <div class="col-1">
                            ${get.rec? `<button class="float-right btn btn-link" type="button" 
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

        return table? `<div class="accordion" id="accordionGets">${table}</div>` : '';
    },
    render: function(index) {
        const profile = GrammarTable.profiles[index];
        
        GrammarTable.showcase.text(profile.parse.join(' '));
        GrammarTable.panel.html(GrammarTable.buildGrammar(profile));
        initVisible();
        
        VocabularyTable.init(profile.sent);
        
        $('#accordionGets > .card').hover((e) => {
            const indices = e.currentTarget.dataset.indices.split(',').map(el => parseInt(el));
            const level = e.currentTarget.dataset.level;
            const tokens = profile.parse.map((token, i) =>
                indices.includes(i) ?
                    '<span class="highlight px-1 ' + level + '">' + token + '</span>' : token
            );
            GrammarTable.showcase.html(tokens.join(' '));
        }, (e) => {
            GrammarTable.showcase.html(GrammarTable.showcase.text());
        });
    },
};
