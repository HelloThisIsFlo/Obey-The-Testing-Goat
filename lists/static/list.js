window.Superlists = {};
window.Superlists.initialize = function() {
  function hideError() {
    $(".has-error").hide();
  }

  $('input[name="text"]').on("keypress", hideError);
  $('input[name="text"]').on("click", hideError);
};
