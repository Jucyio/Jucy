
function ajaxVote(form) {
    var button = form.find('button[name="like"]');
    var loader = form.find('.flaticon-loader');
    button.hide();
    loader.show();
    $.ajax({
	type: 'POST',
	url: form.attr('action'),
	data: {
	    'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val(),
	},
	success: function(data) {
	    form.attr('action', '/_ajax/' + repository + '/ideas/' + (data['vote'] == 'unvote' ? 'vote' : 'unvote') + '/' + (form.closest('.issue').data('issue-number')) + '/');
	    if (data['total_subscribers'] == 0) {
		button.find('.text').text('');
	    } else {
		button.find('.text').text(data['total_subscribers']);
	    }
	    loader.hide();
	    button.show();
	},
	error: function(xhr, ajaxOptions, thrownError) {
	    genericAjaxError(xhr, ajaxOptions, thrownError);
	    loader.hide();
	    button.show();
	},
    });
}

function ajaxSubmit(form) {
    var button = form.find('input[type="submit"]');
    var loader = form.find('.flaticon-loader');
    button.hide();
    loader.show();
    $.ajax({
	type: 'POST',
	url: form.attr('action'),
	data: {
	    'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val(),
	    'title': form.find('input[name="title"]').val(),
	    'content': form.find('input[name="content"]').val(),
	},
	success: function(data) {
	    form.closest('[class^="col-"]').before(data);
	    issueHandler();
	    form.find('input[name="title"]').val('');
	    form.find('input[name="content"]').val('');
	    loader.hide();
	    button.show();
	},
	error: function(xhr, ajaxOptions, thrownError) {
	    genericAjaxError(xhr, ajaxOptions, thrownError);
	    loader.hide();
	    button.show();
	},
    });
}

function issueHandler() {
    $('[href="#messages"]').unbind('click');
    $('[href="#messages"]').click(function(e) {
	e.preventDefault();
	var issue = $(this).closest('.issue');
	var messages = issue.find('.messages');
	issue.find('.details').collapse('show');
	messages.show();
	if (!(issue.find('.messages').hasClass('loaded'))) {
	    $.get('/_ajax/' + repository + '/ideas/comments/' + issue.data('issue-number') + '/', function(data) {
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
			error: genericAjaxError,
			type: 'POST',
			url: 'https://api.github.com/markdown'
		    });
		};
	    });
	}
	return false;
    });
    $('button[name="like"]').unbind('click');
    $('button[name="like"]').click(function(e) {
	e.preventDefault();
	var button = $(this);
	var form = button.closest('form');
	if (authenticated_user == null) {
	    authenticateForm(function() {
		if (authenticated_user['is_collaborator']) {
		    location.reload();
		} else {
		    ajaxVote(form);
		}
	    });
	} else {
	    ajaxVote(form);
	}
	return false;
    });
}

$(document).ready(function() {
    issueHandler();

    $('form#submit').submit(function(e) {
	e.preventDefault();
	var form = $(this);
	if (authenticated_user == null) {
	    authenticateForm(function() {
		if (authenticated_user['is_collaborator']) {
		    location.reload();
		} else {
		    ajaxSubmit(form);
		}
	    });
	} else {
	    ajaxSubmit(form);
	}
	return false;
    });
});
