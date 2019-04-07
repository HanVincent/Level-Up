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
//         exampleBtn.button('loading');
        Example.getExampleButton(ngramstr, exampleBtn, exampleRow);
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
  getExample: function(ngramstr, exampleBtn, exampleRow, url = Example.API) {
    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify({ngram: ngramstr}),
      contentType: "application/json",
      dataType: 'json',
    }).done(function(data) {
      exampleRow.html(Example.render(data.ngram, data.examples));
      exampleRow.data('fetched', "true");
    }).fail(function(data) {
      exampleRow.html('No result.');
    }).always(function() {
      exampleRow.show();
      exampleBtn.text('Hide');
      exampleRow.data('hide', false);
      // this.exampleLock = false;
    });
  },
  getExampleButton: function(ngramstr, exampleBtn, exampleRow) {
    return (function(){
      Example.getExample(ngramstr, exampleBtn, exampleRow);
    })(ngramstr, exampleBtn, exampleRow);
  },
  /* Highlight the ngram string in the example (used in `render` function)*/
  highlight: function(ngramstr, example) {
//     var regexp = new RegExp(ngramstr, 'ig');
//     return example.replace(regexp, '<span class="highlight">$&</span>')
      return example;
  },
  /* Convert array of example string to HTML string */
  render: function(ngramstr, examples) {
    // TODO: need some design
//     return `<td colspan="4"><ul>${examples.map((example) => `<li>${this.highlight(ngramstr, example)}</li>`).join('')}</ul></td>`;
      return examples.map((example) => `<li>${capitalize(this.highlight(ngramstr, example))}</li>`).join('')
  }
};
