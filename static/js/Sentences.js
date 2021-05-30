'use strict';

const Sentences = {
  API: '/sentences',

  initSentenceBtns: function () {
    $('.btn-sentence').on('click', function () {
      const sentenceBtn = $(this);
      const no = sentenceBtn.data('no');
      const index = sentenceBtn.data('index');
      const ngram = sentenceBtn.data('ngram');
      const sentenceRow = $('#ngram-' + no + '-' + index);


      if (!sentenceRow.data('fetched')) {
        sentenceBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
        Sentences.getSentences(ngram, sentenceBtn, sentenceRow);
      } else {
        sentenceRow.toggle();
        if (!sentenceRow.data('hide')) {
          sentenceBtn.text('Show');
          sentenceRow.data('hide', true);
        } else {
          sentenceBtn.text('Hide');
          sentenceRow.data('hide', false);
        }
      }
    });
  },
  getSentences: function (ngram, sentenceBtn, sentenceRow, url = Sentences.API) {
    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify({ ngram }),
      contentType: "application/json",
      dataType: 'json',
    }).done(function (response) {
      sentenceRow.data('fetched', "true");
      if (response.sentences.length === 0) { sentenceRow.html('<i>No result.</i>'); }
      else { sentenceRow.html(Sentences.render(ngram, response.sentences)); }
    }).always(function () {
      sentenceRow.show();
      sentenceBtn.text('Hide');
      sentenceRow.data('hide', false);
    });
  },
  render: function (ngram, sentences) {
    return sentences.map((sentence) => `<li class="m-1">${capitalize(sentence)}</li>`).join('')
  }
};
