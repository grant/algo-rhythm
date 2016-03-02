$(document).ready(function(){
  // Always be scrolled to the top on page load
  setTimeout(function() {
    $(this).scrollTop(0);
  }, 0);

  // Remove query parameters
  history.replaceState(null, "", location.href.split("?")[0]);

  // Setup event handlers
  $('.section.generated-music .song:not(.header)').click(function() {
    var songName = $(this).data('name');
    console.log('toggle: ', songName);
    $(this).toggleClass('playing');
  });

  $('.section.upload input[type="file"]').on('change', function() {
    $('.section.upload .form').submit();
  });
});