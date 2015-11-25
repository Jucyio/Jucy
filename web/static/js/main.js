$(function() {
    $('a.page-scroll').bind('click', function(event) {
	var $anchor = $(this);
	$('html, body').stop().animate({
	    scrollTop: $($anchor.attr('href')).offset().top
	}, 1500, 'easeInOutExpo');
	event.preventDefault();
    });
    $('.emojione-render').each(function() {
	$(this).html(emojione.toImage($(this).text()));
    });
    $('.marked').each(function() {
	$(this).html(marked($(this).html()));
    });
});
