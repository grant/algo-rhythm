$(document).ready(function(){
  // Always be scrolled to the top on page load
  setTimeout(function() {
    $(this).scrollTop(0);
  }, 0);

  // Setup event handlers
  $('.generated-music .song:not(.header)').click(function() {
    var songName = $(this).data('name');
    console.log('toggle: ', songName);
    $(this).toggleClass('playing');
  });
});