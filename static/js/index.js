'use strict';

$(document).ready(() => {
    const overlaySuggest = $('#overlay-suggest');
    const overlayGrammar = $('#overlay-grammar');
    const overlayVocab = $('#overlay-vocab');
    const urlInput = $('#url-input');
    const contentBlock = $('#content-block');
    const showcase = $('#showcase');
    const suggestDiv = $('#main-suggest');
    const grammarDiv = $('#main-grammar');
    const vocabDiv = $('#main-vocab');
    const multiSelect = $('#category-select');

    $('#btn-url-search').click(e => {
        e.preventDefault();
        
        const url = urlInput.val().trim();
        console.log(url);
        if (url) {
            request("/profiling", { 'content': url, 'access': 'url' }, overlayGrammar).done(main);
        }
    });
    
    $('#btn-submit').click(e => {
        e.preventDefault();

        const content = contentBlock.text().trim();
        if (content) {
            request("/profiling", { 'content': content, 'access': 'text'}, overlayGrammar).done(main);
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

        $(e.currentTarget).tooltip('show');
        setTimeout(() => {$(e.currentTarget).tooltip('hide')}, 1500);
    });
    
    $('#btn-setting').click(e => {
        e.preventDefault();
    });
    
    $('#btn-update-setting').click(e => {
        e.preventDefault();
        
        updateSetting();
        
        renderGrammar(window.profiles[window.sentenceIndex]);
        renderVocab(window.vocabs);
    });

    $('#nav-grammar-tab').on('click', function (e) {
        e.preventDefault()
        if (!window.profiles) return;

        showcase.html(showcase.text());
    });

    $('#nav-vocab-tab').on('click', function (e) {
        e.preventDefault()
        if (!window.vocabs) return;

        showcase.html(showcase.text());
    });

    window.checkedCategory = ['ADJECTIVES', 'ADVERBS', 'CLAUSES']; // default selected
    multiSelect.selectpicker('val', window.checkedCategory);
    multiSelect.on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        window.checkedCategory = multiSelect.val();
                
        updateSetting();
        
        renderGrammar(window.profiles[window.sentenceIndex]);
        renderVocab(window.vocabs);
    });
    
    contentBlock.on('input', debounce(function() {
        const content = contentBlock.text().trim();
        request("/suggesting", { 'content': content }, overlaySuggest).done(renderSuggest);
    }, 500));
    
    contentBlock.click(e => {
        e.preventDefault();

        if (e.target.tagName === "SPAN") {
            flow(e.target.dataset.sentenceIndex);
        }
    });

    
    function updateSetting() {
        window.checkedGrammar = $("input[name='grammar-setting']:checked").map(function() {return this.value}).toArray();
        window.checkedVocab = $("input[name='vocab-setting']:checked").map(function() {return this.value}).toArray();
    }
    
    
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
        window.sentenceIndex = profileIndex;
        
        updateSetting();
        
        // render showcase
        renderShowcase(profile);
        
        // render grammar table
        renderGrammar(profile);

        // render vocabulary section
        if (profile.sent) {
            request("/vocabuing", { 'sentence': profile.sent }, overlayVocab)
                .done(response => {
                    window.vocabs = response.vocabs.map((token, i) => Object.assign(token, {index: i}));
                    renderVocab(window.vocabs);
                });
        }
    }
    
    function renderSuggest(response) {
        $('#nav-suggest-tab').tab('show');
        
        const suggestions = response.suggest;
        if (!suggestions || suggestions.length == 0) {
            suggestDiv.html('');            
        } else {
            const suggestTable = buildSuggestTable(suggestions);
            suggestDiv.html(suggestTable);   
        }
        
        Example.initExampleBtns();
        $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
    }

    function renderShowcase(profile) {
        showcase.text(profile.parse.join(' '));
    }

    function renderGrammar(profile) {
        $('#nav-grammar-tab').tab('show');
        
        grammarDiv.html(buildGrammarTable(profile));

        $('#accordionGets > .card').hover((e) => {
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

        $('#accordionVocabs > .card').hover((e) => {
            const index = parseInt(e.currentTarget.dataset.index);
            const level = e.currentTarget.dataset.level;

            const tokens = vocabs.map((token, i) => i == index? 
                                      `<span class="highlight px-1 ${level}">${token.token}</span>` : token.token);
            showcase.html(tokens.join(' '));
        }, (e) => {
            showcase.html(showcase.text());
        });
        
        $(() => { $('[data-toggle="tooltip"]').tooltip() }); // initiate
    }
})