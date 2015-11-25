
$(document).ready(function() {
    $('[href="#messages"]').click(function(e) {
	e.preventDefault();
	var issue = $(this).closest('.issue');
	var messages = issue.find('.messages');
	issue.find('.details').collapse('show');
	messages.show();
	if (!(issue.find('.messages').hasClass('loaded'))) {
	    $.get('/' + repository + '/_ajax/issue/' + issue.data('issue-number') + '/comments', function(data) {
		messages.addClass('loaded');
		messages.html(data);
		messages.find('.marked').each(function() {
		    $(this).html(marked($(this).html()));
		});
	    });
	}
	return false;
    });
});
