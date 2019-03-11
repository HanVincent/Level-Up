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
function uniq(elements) {
    const cacheTable = {};
    const newGets = [];
    let i = 0;
    for (let el of elements) {
        if (cacheTable.hasOwnProperty(el.no)) {
            newGets[cacheTable[el.no]].indices.push(...el.indices);
        } else {
            newGets.push(el);
            cacheTable[el.no] = i++;
        }
    }
    return newGets
}

function buildGrammarTable(profile) {
    const { gets, recs } = profile;

    const table = uniq(gets).filter(get => window.checkedGrammar.includes(get.level)).reduce((getsPrev, get, i) => {
        const recsList = recs[i] || [];
        const recRows = recsList.reduce((recsPrev, rec) =>
            recsPrev + `
            <ul class="pl-4 pb-1">
                <li>
                    <span class="badge ${rec.level}" data-toggle="tooltip" data-placement="top" title="${rec.category} ${rec.subcategory}">
                        ${rec.level}
                    </span>
                    ${rec.statement} 
                    <number>${rec.no}</number>

                    <div class="px-2 py-1 mt-2 text-monospace bg-light">
                        <small>${rec.highlight}</small>
                    </div>
                </li>
            </ul>`, '');

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
                    ${!!recRows ? recRows : '<tr>No recommend</tr>'}
                </div>
            </div>
        </div>`}, '');

    return `
    <div class="accordion" id="accordionGets">
        ${table}
    </div>`
}

function buildVocabTable(vocabs) {
    const table = vocabs.filter(vocab => vocab.level).filter(vocab => window.checkedVocab.includes(vocab.level)).reduce((prev, vocab, i) => {
        // const recsList = recs[i] || [];
        // const recRows = recsList.reduce((recsPrev, rec) =>
        //     recsPrev + `
        //     <ul class="pl-4 pb-1">
        //         <li>
        //             <span class="badge ${rec.level}" data-toggle="tooltip" data-placement="top" title="${rec.category} ${rec.subcategory}">
        //                 ${rec.level}
        //             </span>
        //             ${rec.statement} 
        //             <number>${rec.no}</number>

        //             <div class="px-2 py-1 mt-2 text-monospace bg-light">
        //                 <small>${rec.highlight}</small>
        //             </div>
        //         </li>
        //     </ul>`, '');

        return prev + `
        <div class="card border-right-0 border-left-0" data-level="${vocab.level}">
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