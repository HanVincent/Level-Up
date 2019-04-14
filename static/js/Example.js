'use strict';

const Example = {
  API: '/examples',

  initExampleBtns: function() {
    $('.btn-sentence').on('click', function(){
      const exampleBtn = $(this);
      const no = exampleBtn.data('no');
      const index = exampleBtn.data('index');
      const ngramstr = exampleBtn.data('ngram');
      const exampleRow = $('#ngram-' + no + '-' + index);
        
        
      if(!exampleRow.data('fetched')) {
        exampleBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
        Example.getExample(ngramstr, exampleBtn, exampleRow);
      } else {
        exampleRow.toggle();
        if(!exampleRow.data('hide')) {
          exampleBtn.text('Show');
          exampleRow.data('hide', true);
        } else {
          exampleBtn.text('Hide');
          exampleRow.data('hide', false);
        }
      }
    });
  },
  getExample: function(ngramstr, exampleBtn, exampleRow, url=Example.API) {
    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify({ngram: ngramstr}),
      contentType: "application/json",
      dataType: 'json',
    }).done(function(response) {
      exampleRow.data('fetched', "true");
      if (response.examples.length === 0) { exampleRow.html('<i>No result.</i>'); }
      else { exampleRow.html(Example.render(response.ngram, response.examples));}
    }).always(function() {
      exampleRow.show();
      exampleBtn.text('Hide');
      exampleRow.data('hide', false);
    });
  },
  render: function(ngramstr, examples) {
      return examples.map((example) => `<li>${capitalize(example)}</li>`).join('')
  }
};
