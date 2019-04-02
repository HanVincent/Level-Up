function buildSentences(profiles) {
    const sentences = profiles.map((curr, i) => {
        const { sent } = curr;

        return `<span id="span-${i}" class="sent hoverable" data-sentence-index="${i}">
                ${sent} 
            </span>`
    })

    return sentences.join(' ');
}

// TODO: refactor
function uniq(gets, recs) {
    const cacheTable = {};
    const newGets = [];
    let i = 0;
    gets.forEach((get, index) => {
        if (cacheTable.hasOwnProperty(get.no)) {
            newGets[cacheTable[get.no]].indices.push(...get.indices);
        } else {
            newGets.push(Object.assign(get, {rec: recs[index]}));
            cacheTable[get.no] = i++;
        }
    })
    return newGets
}

function buildSuggestTable(suggestions) {
    
    const template = suggestions.sort((a, b) => b.lm - a.lm).reduce((prev, curr) => {
        const lis = curr.ngrams.reduce((prev_li, ngram) => {
            return prev_li + `<li><i>${ngram}</i></li>`
        }, '');
        
        return prev + `<div>
                            <div class="row font-weight-bold">
                                <div class="col-8">
                                    <span class="badge ${curr.level}">
                                        ${curr.level}
                                    </span>
                                    <span>[${curr.pos}] ${curr.pattern}</span>
                                    <number>${curr.no}</number>
                                </div>
                                <div class="col-4 text-right">
                                    <span class="text-info">${(curr.lm * 100).toFixed(2)} %</span>
                                </div>
                            </div>

                            <ul>${lis}</ul>

                            <div class="row d-none">
                                <div class="col-2"></div>
                                <div class="col-10">${curr.sentence}</div>
                            </div>
                        </div>`;
            
            curr.join(' ');
    }, '');
    
    return template;
}

function buildGrammarTable(profile) {
    const { gets, recs } = profile;

    const table = uniq(gets, recs).filter(get => window.checkedGrammar.includes(get.level) && window.checkedCategory.includes(get.category)).reduce((getsPrev, get, i) => {
        const recRow =  get.rec? `
            <ul class="pl-4 pb-1">
                <li>
                    <span class="badge ${get.rec.level}" data-toggle="tooltip" data-placement="top" title="${get.rec.category} ${get.rec.subcategory}">
                        ${get.rec.level}
                    </span>
                    ${get.rec.statement} 
                    <number>${get.rec.no}</number>

                    <div class="px-2 py-1 mt-2 text-monospace bg-light">
                        <small>${get.rec.example}</small>
                    </div>
                </li>
            </ul>` : '<tr>No recommend</tr>'
        
        return getsPrev + `
        <div class="card border-right-0 border-left-0" data-indices="${get.indices.join(',')}" data-level="${get.level}">
            <div class="card-header ${get.category} row no-gutters align-items-center p-2" id="card-head-${i}">
                <div class="col-1">
                    <span class="badge ${get.level}" data-toggle="tooltip" data-placement="top" title="${get.category} ${get.subcategory}">
                        ${get.level}
                    </span>
                </div>
                <div class="col-10">
                    ${get.statement} 
                    <number>${get.no}</number>
                </div>
                <div class="col-1">
                    <button class="float-right btn btn-link" type="button" data-toggle="collapse" data-target="#collapse-get-${i}" aria-expanded="true" aria-controls="collapse-get-${i}">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        
            <div id="collapse-get-${i}" class="collapse" aria-labelledby="card-head-${i}" data-parent="#accordionGets">
                <div class="card-body p-2">
                    ${recRow}
                </div>
            </div>
        </div>`}, '');

    return `
    <div class="accordion" id="accordionGets">
        ${table}
    </div>`
}

function buildVocabTable(vocabs) {
    const table = vocabs.filter(vocab => vocab.level && window.checkedVocab.includes(vocab.level)).reduce((prev, vocab, i) => {
        return prev + `
        <div class="card border-right-0 border-left-0" data-index="${vocab.index}"  data-level="${vocab.level}">
            <div class="card-header row no-gutters align-items-center p-2" id="card-head-${i}">
                <div class="col-1">
                    <span class="badge ${vocab.level}">
                        ${vocab.level}
                    </span>
                </div>
                <div class="col-10">${vocab.token}</div>
                <div class="col-1">
                    <button class="float-right btn btn-link" type="button" data-toggle="collapse" data-target="#collapse-vocab-${i}" aria-expanded="true" aria-controls="collapse-vocab-${i}">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        
            <div id="collapse-vocab-${i}" class="collapse" aria-labelledby="card-head-${i}" data-parent="#accordionVocabs">
                <div class="card-body p-2">
                    <tr>No recommend</tr>
                </div>
            </div>
        </div>`}, '');

    return `
    <div class="accordion" id="accordionVocabs">
        ${table}
    </div>`
}