
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
		if ($(this).html() != null)
		{
		    var that = this;
		    $.ajax({
			contentType: 'application/json',
			data: JSON.stringify({
			    "text": $(this).html(),
			    "mode": "gfm",
			    "context": repository
			}),
			dataType: 'html',
			success: function(data){
			    $(that).html(data);
			},
			error: function(){
			},
			type: 'POST',
			url: 'https://api.github.com/markdown'
		    });
		};
	    });
	}
	return false;
    });
    $('[href="#like"]').click(function(e) {
	e.preventDefault();
	if (authenticated_user == null) {
	    authenticateForm(function() {
		console.log('Todo ajax vote');
		if (authenticated_user['is_collaborator']) {
		    location.reload();
		}
	    });
	} else {
	    console.log('Todo ajax vote');
	}
	return false;
    });
});
