'use strict';

const SuggestTable = {
    API: '/suggesting',
    overlay: $('#overlay-suggest'),
    panel: $('#main-suggest'),

    init: function() {
        $('#content-block').on('input', debounce(function() {
            const content = this.innerText.replace(/(\s+)|(&nbsp;)/g," ").trim();
            SuggestTable.getSuggestions(content);

        }, 500));
        
        // TODO: remove
        const content = $('#content-block')[0].innerText.replace(/(\s+)|(&nbsp;)/g," ").trim();
        SuggestTable.getSuggestions(content);
    },
    getSuggestions: function(content, url=SuggestTable.API){
        $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify({content: content}),
            contentType: "application/json",
            dataType: 'json',
            beforeSend: () => { 
                $('#nav-suggest-tab').tab('show');
                SuggestTable.overlay.removeClass('d-none'); 
            }
        }).done(function(response) {
            if (response.suggestions.length == 0) { 
                SuggestTable.panel.text(''); 
            } else { 
                SuggestTable.panel.html(SuggestTable.render(response.get, response.suggestions)); 
            }
        }).always(function() {
            initVisible();
            $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
            
            $('.btn-ngrams').on('click', function(){
                const ngramsBtn = $(this);
                const index = ngramsBtn.data('index');
                const ngramsRow = $('#ngrams-' + index);

                ngramsRow.toggle();
              });
            Example.initExampleBtns();
            SuggestTable.overlay.addClass('d-none');
        })
    },
    buildDetect: function(get) {
        if (!get) {return '<span class="align-middle">NO rules detected.</span>'}

        const tooltip = `<h6 class='m-0'>${get.category}</h6>
                         <p class='m-0'> ${get.subcategory}</p>`
        return `<span class="badge ${get.level}" title="${tooltip}"
                      data-toggle="tooltip" data-placement="top" data-html=true>
                      ${get.level}
                </span>
                <span class="help-tip" data-toggle="tooltip" data-placement="top" 
                      data-html=true title="<p class='m-0'>${get.statement}</p>">
                </span>
                <span class="align-middle">${get.pattern}</span>
                <small>(${get.ngram})</small>` 
    },
    buildSuggestions: function(suggestions) {
        return suggestions.patterns.concat(suggestions.collocations)
            .map((curr, i) => {
                const tooltipBadge = `<h6 class='m-0'>${curr.category}</h6>
                                      <p class='m-0'>${curr.subcategory}</p>`;
                const tooltipHelp = `<p class='m-0'>${curr.statement}</p>`;

                const ngramsSec = curr.ngrams.map((ngram, j) => `
                    <li>
                        <span>${ngram}</span>
                        <a href="#" class="small btn-sentence float-right" 
                           data-no="${curr.no}" data-index="${j}" data-ngram="${ngram}">
                           Show</a>
                    </li>

                    <ul id="ngram-${curr.no}-${j}" style="display: none;" 
                        class="px-4 py-1 my-2 bg-light"
                        data-fetched="false" data-hide="true"></ul>
                `).join('');
            
                return `<div class="${getLevelCategory(curr.level)}-visible">
                            <div class="row btn-ngrams hoverable" 
                                 data-index="${i}" data-no="${curr.no}">
                                <div class="col mb-1">
                                    <span class="badge ${curr.level}" data-toggle="tooltip" 
                                          data-placement="top" data-html=true
                                          title="${tooltipBadge}">${curr.level}</span>

                                    <span class="help-tip" data-toggle="tooltip" data-placement="top" 
                                          data-html=true title="${tooltipHelp}"></span>

                                    <span class="font-weight-bold align-middle">${curr.pattern}</span>
                                    <span class="text-secondary align-middle">(${curr.ngram})</span> 
                                </div>
                            </div>

                            <ul id="ngrams-${i}" style="display: none;">${ngramsSec}</ul>
                        </div>`;
            });
    },
    render: function(get, suggestions) {
        return `<h5 class="font-weight-bold p-2 mb-3 text-dark" style="background-color: #e3f2fd;">
                    <span class="align-middle mr-1">Detected:</span>
                    ${ SuggestTable.buildDetect(get) }
                </h5>` + SuggestTable.buildSuggestions(suggestions).join('');
    },
};
