window.Superlists = {};
window.Superlists.initialize = function(url) {
  function hideError() {
    $(".has-error").hide();
  }

  $('input[name="text"]').on("keypress", hideError);
  $('input[name="text"]').on("click", hideError);

  $.get(url).done(function(response) {
    function buildRow(index, text) {
      return `<tr><td>${index}: ${text}</td></tr>`;
    }

    const rows = [];
    response
      .map((item, index) => buildRow(index + 1, item.text))
      .forEach(row => rows.push(row));
    
    $('#id_list_table').html(rows)
  });
};
