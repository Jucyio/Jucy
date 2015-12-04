
var loader_html = '<i class="flaticon-loader fontx1-5"></i>';

function freeModal(title, body, buttons) {
    $('#freeModal .modal-header h4').html(title);
    $('#freeModal .modal-body').html(body);
    $('#freeModal .modal-footer').html('<button type="button" class="btn btn-jucy" data-dismiss="modal">Go</button>');
    $('#freeModal .modal-footer button').unbind('click');
    if (buttons === 0) {
	$('#freeModal .modal-footer').hide();
    } else if (typeof buttons != 'undefined') {
	$('#freeModal .modal-footer').html(buttons);
	$('#freeModal .modal-footer').show();
    }
    $('#freeModal').modal('show');
}

function genericAjaxError(xhr, ajaxOptions, thrownError) {
    alert(xhr.responseText);
}

function _authenticateForm_onSubmit(cb) {
    $('#freeModal form').unbind('submit');
    $('#freeModal form').submit(function(e) {
	e.preventDefault();
	if ($('#freeModal #id_email').val()) {
	    $('#freeModal input[type=submit]').replaceWith(loader_html);
	    $(this).ajaxSubmit({
		success: function(data) {
		    if (data['redirect']) {
			window.location.href = data['redirect'];
		    } else if (data['username']) {
			authenticated_user = data;
			if (authenticated_user['github']) {
			    $('#authenticated_username').text(authenticated_user['username']);
			} else {
			    $('#authenticated_username').text(authenticated_user['email']);
			}
			$('.hidden-when-authenticated').hide();
			$('#authenticated').removeClass('hidden');
			if (typeof(cb) != 'undefined') {
			    cb();
			}
			$('#freeModal').modal('hide');
		    } else {
			var html = $(data);
			$('#freeModal .modal-body').html(html.html());
			_authenticateForm_onSubmit();
		    }
		},
		error: genericAjaxError,
	    });
	}
    });
}

function authenticateForm(cb) {
    $('#authenticate_form #id_email').prop('required', true);
    freeModal('<br>', $('#authenticate_form').html(), 0);
    _authenticateForm_onSubmit(cb);
}

$(function() {
    $('a.page-scroll').bind('click', function(e) {
	var $anchor = $(this);
	$('html, body').stop().animate({
	    scrollTop: $($anchor.attr('href')).offset().top
	}, 1500, 'easeInOutExpo');
	e.preventDefault();
	return false;
    });
    $('.emojione-render').each(function() {
	$(this).html(emojione.toImage($(this).text()));
    });
    $('.marked').each(function() {
	$(this).html(marked($(this).html()));
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
    $('[data-modal-authenticate="true"]').click(function(e) {
	e.preventDefault();
	authenticateForm();
	return false;
    });
});
