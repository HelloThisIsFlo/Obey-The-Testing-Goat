window.Superlists = {};
window.Superlists.updateItems = function(url) {
  $.get(url).done(function(response) {
    function buildRow(index, text) {
      return `<tr><td>${index}: ${text}</td></tr>`;
    }

    const rows = [];
    response.items
      .map((item, index) => buildRow(index + 1, item.text))
      .forEach(row => rows.push(row));

    $("#id_list_table").html(rows);
  });
};
window.Superlists.initialize = function(params) {
  function hideError() {
    $(".has-error").hide();
  }

  $('input[name="text"]').on("keypress", hideError);
  $('input[name="text"]').on("click", hideError);

  if (params) {
    window.Superlists.updateItems(params.listApiUrl);

    const form = $("#id_item_form");
    form.on("submit", function(event) {
      event.preventDefault();
      $.post(params.itemsApiUrl, {
        list: params.listId,
        text: form.find('input[name="text"]').val(),
        csrfmiddlewaretoken: form
          .find('input[name="csrfmiddlewaretoken"]')
          .val()
      })
        .done(function(response) {
          $(".has-error").hide();
          window.Superlists.updateItems(params.listApiUrl);
        })
        .fail(function(xhr) {
          $(".has-error").show();
          if (xhr.responseJSON && xhr.responseJSON.error) {
            $(".has-error .help-block").text(xhr.responseJSON.error);
          } else {
            $(".has-error .help-block").text(
              "Error talking to server. Please try again."
            );
          }
        });
    });
  }
};
