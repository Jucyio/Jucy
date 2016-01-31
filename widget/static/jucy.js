var jucy_service_name = (typeof jucy_service_name == 'undefined' ? 'the site' : jucy_service_name);
var jucy_api_url = (typeof jucy_api_url == 'undefined' ? 'http://jucy.io/_api/' : jucy_api_url);
var jucy_website_url = (typeof jucy_website_url == 'undefined' ? 'http://jucy.io/' : jucy_website_url);
var jucy_default_tab = (typeof jucy_default_tab == 'undefined' ? 'jucy-home' : jucy_default_tab);
var jucy_debug = (typeof jucy_debug == 'undefined' ? false : jucy_debug);
var jucy_help_link = (typeof jucy_help_link == 'undefined' ? 'http://github.com/' + jucy_repository + '/wiki/' : jucy_help_link);
var jucy_corner_widget = (typeof jucy_corner_widget == 'undefined' ? true : jucy_corner_widget);

if (typeof jucy_repository == 'undefined' || !jucy_repository) {
    console.log('Please specify the jucy_repository variable in order for jucy to work. Learn more: http://jucy.io/');
    var jucy_repository = '';
}

var jucy_authenticated_user = false;

var jucy_footer = '<div class="jucy-footer"><a href="#jucy-ideas">Suggest an idea</a><a href="#jucy-help">Ask a question</a><a href="#jucy-contact">Contact us</a><a href="http://jucy.io/" target="_blank" class="jucy-watermark">powered by <span class="jucy-logo">jucy</span> <img src="http://jucy.io/_static/img/jucy.svg" alt="jucy"></a></div>';

var jucy_thank_you = '<div class="jucy-thank-you"><div class="jucy-thank-you-title">Thank you.</div><div class="jucy-thank-you-content">We will get back to you as soon as possible.</div</div>';

var jucy_error = '<div class="jucy-error" style="display: none"></div>';

var jucy_tabs = {
    'jucy-home': '<div class="jucy-actions"><a href="#" class="jucy-action jucy-ideas"><br><span>Ideas</span><p>Decide what\'s next on ' + jucy_service_name + ' & share your ideas or report bugs</p></a><a href="#" class="jucy-action jucy-help"><br><span>Help</span><p>Ask a question & discover how to use ' + jucy_service_name + '</p></a><a href="#" class="jucy-action jucy-contact"><br><span>Contact</span><p>Any personal inquiry? Contact us privately.</p></a></div>',
    'jucy-ideas': '<div class="jucy-loader"></div><h4 class="jucy-ideas-title" style="display: none;">What do you want to see next on ' + jucy_service_name + '?</h4><div class="jucy-ideas-vote" style="display:none"><div class="jucy-vote-idea jucy-left-idea"><div class="jucy-panel"><h6 class="jucy-idea-title"></h6><a href="#ideaDetails" class="jucy-idea-details-button">+ details</a><div class="jucy-idea-details" style="display:none"></div><a href="#jucyVote" class="jucy-idea-vote-button"></a></div><a href="' + jucy_website_url + jucy_repository + '/ideas/" class="jucy-ideas-more jucy-external-link" style="display: none;/*todo*/">+ more</a></div><div class="jucy-vote-idea jucy-right-idea"><div class="jucy-panel"><h6 class="jucy-idea-title"></h6><a href="#ideaDetails" class="jucy-idea-details-button">+ details</a><div class="jucy-idea-details" style="display:none"></div><a href="#jucyVote" class="jucy-idea-vote-button"></a></div><a href="' + jucy_website_url + jucy_repository + '/ideas/" class="jucy-ideas-more jucy-external-link" style="display: none;/*todo*/">+ more</a></div><div class="jucy-ideas-buttons"><a href="#jucy-suggest-idea" class="jucy-suggest-idea"><span class="jucy-or" style="display:none">or</span> Suggest an idea</a> <a href="' + jucy_website_url + jucy_repository + '/" target="_blank" class="jucy-browse-ideas jucy-external-link"><span class="jucy-or">or</span> Browse all the ideas</a></div></div><div class="jucy-suggest-idea-form" style="display:none"><input type="text" class="jucy-submit-idea-title" maxlength="1023" placeholder=\'Example: \"Add a subscribe button to receive news by email\"\' required /><textarea class="jucy-submit-idea-content" style="display: none" placeholder="More details about your idea"></textarea><a href="#jucySubmitMore" class="jucy-submit-idea-more">More</a><input type="submit" class="jucy-submit-idea" value="Submit"><div class="jucy-loader-small" style="display: none"></div><div class="jucy-ideas-buttons"><a href="#jucy-vote-ideas" class="jucy-vote-ideas"><span class="jucy-or" style="display:none">or</span> Vote for the next ideas</a> <a href="' + jucy_website_url + jucy_repository + '/" target="_blank" class="jucy-browse-ideas jucy-external-link"><span class="jucy-or">or</span> Browse all the ideas</a></div></div>',
    'jucy-help': '<a href="' + jucy_help_link + '" target="_blank">Visit our wiki to get help</a>',
    'jucy-contact': '<div class="jucy-contact-form"><textarea class="jucy-contact-message" placeholder="Your message"></textarea><div class="jucy-loader-small" style="display: none"></div><input type="submit" class="jucy-submit-message" value="Submit"></div>',
};

function jucy_show_error(error_text) {
    $('.jucy-error').remove();
    var error = $(jucy_error);
    error.html(error_text);
    $('#jucy-content').prepend(error);
    error.show('fast');
}

function jucy_ajax_error(xhr, ajaxOptions, thrownError) {
    var error_text = 'A gigantic monster drank all the internet juice and we couldn\'t fullfil your request. Please try again!';
    try {
	error_text = JSON.parse(req.responseText);
    } catch (e) {}
    if (jucy_debug) {
	jucy_show_error(error_text + '<br><br>' + xhr.responseText);
    } else {
	jucy_show_error(error_text);
    }
}

var jucy_random_vote_sentences = [
    'I like this idea!',
    'Make it so!',
    'Sounds good!',
    'Yes, yes, yes!',
    'Go for it!',
    'Yes, please!',
];

function jucy_random_vote_sentence() {
    return jucy_random_vote_sentences[Math.floor(Math.random() * jucy_random_vote_sentences.length)];
}

function jucy_load_idea_panel(panel, issue) {
    panel.find('.jucy-idea-title').text(issue['title']);
    if (issue['body']) {
	panel.find('.jucy-idea-details').text(issue['body']);
	panel.find('.jucy-idea-details-button').click(function(e) {
	    e.preventDefault();
	    panel.find('.jucy-idea-details').toggle('fast');
	    if (!(panel.find('.jucy-idea-details').hasClass('marked'))) {
		$.ajax({
		    type: 'POST',
		    url: 'https://api.github.com/markdown',
		    data: JSON.stringify({
			'text': issue['body'],
			'mode': 'gfm',
			'context': jucy_repository,
		    }),
		    success: function(data) {
			panel.find('.jucy-idea-details').html(data);
			panel.find('.jucy-idea-details').addClass('marked');
		    },
		    error: jucy_ajax_error,
		});
	    }
	    return false;
	});
    } else {
	panel.find('.jucy-idea-details-button').hide();
    }
    panel.find('.jucy-idea-vote-button').text(jucy_random_vote_sentence());
    panel.find('.jucy-idea-vote-button').click(function(e) {
	e.preventDefault();
	jucy_test_authentication(function() {
	    $.ajax({
		type: 'POST',
		url: jucy_api_url + jucy_repository + '/ideas/vote/' + issue['number'] + '/',
		success: function(data) {
		    jucy_change_tab('jucy-ideas');
		},
		error: jucy_ajax_error,
	    });
	});
	return false;
    });
    panel.find('.jucy-ideas-more').attr('href', panel.find('.jucy-ideas-more').attr('href') + issue['number'] + '/');
}

var jucy_tabs_callbacks = {
    'jucy-home': function() {
	$('.jucy-footer a[href^="#jucy-"]').hide();
	$('#jucy-box .jucy-action').click(function(e) {
	    e.preventDefault();
	    var content = $('#jucy-content');
	    var tab = $(this).attr('class').replace('jucy-action ', '');
	    content.html(jucy_tabs[tab]);
	    jucy_tabs_callbacks[tab]();
	    return false;
	});
    },
    'jucy-ideas': function() {
	$('.jucy-footer a[href^="#jucy-"]').show();
	$('.jucy-footer a[href="#jucy-ideas"]').hide();
	$('.jucy-suggest-idea').click(function(e) {
	    e.preventDefault();
	    $('.jucy-ideas-vote').hide('fast');
	    $('.jucy-suggest-idea-form').show('fast');
	    return false;
	});
	$('.jucy-vote-ideas').click(function(e) {
	    e.preventDefault();
	    $('.jucy-suggest-idea-form').hide('fast');
	    $('.jucy-ideas-vote').show('fast');
	    return false;
	});
	$('.jucy-submit-idea-more').click(function(e) {
	    e.preventDefault();
	    $('.jucy-submit-idea-content').toggle('fast');
	    return false;
	});
	$('.jucy-submit-idea').click(function(e) {
	    e.preventDefault();
	    if ($('.jucy-submit-idea-title').val()) {
		var title = $('.jucy-submit-idea-title').val();
		var content = $('.jucy-submit-idea-content').val();
		jucy_test_authentication(function() {
		    $('.jucy-submit-idea').hide();
		    $('.jucy-loader-small').show();
		    $.ajax({
			method: 'POST',
			url: jucy_api_url + jucy_repository + '/ideas/create/',
			data: {
			    title: title,
			    content: content,
			},
			success: function(data) {
			    $('#jucy-content').html(jucy_thank_you);
			},
			error: function(a, b, c) {
			    jucy_ajax_error(a, b, c);
			    $('.jucy-submit-idea').show();
			    $('.jucy-loader-small').hide();
			},
		    });
		});
	    }
	    return false;
	});
	$.ajax({
	    method: 'GET',
	    url: jucy_api_url + jucy_repository + '/ideas/random/',
	    success: function(data) {
		$('.jucy-loader').hide('fast');
		$('.jucy-ideas-title').show('fast');
		if (data['issues'] != null) {
		    $('.jucy-or').show();
		    jucy_load_idea_panel($('.jucy-left-idea'), data['issues'][0]);
		    jucy_load_idea_panel($('.jucy-right-idea'), data['issues'][1]);
		    jucy_external_links();
		    $('.jucy-ideas-vote').show('fast');
		} else {
		    $('.jucy-ideas-vote').hide('fast');
		    $('.jucy-suggest-idea-form').show('fast');
		    $('.jucy-vote-ideas').hide();
		}
	    },
	    error: jucy_ajax_error,
	});
    },
    'jucy-help': function() {
	$('.jucy-footer a[href^="#jucy-"]').show();
	$('.jucy-footer a[href="#jucy-help"]').hide();
	window.open(jucy_help_link, '_blank');
	jucy_close();
    },
    'jucy-contact': function() {
	$('.jucy-footer a[href^="#jucy-"]').show();
	$('.jucy-footer a[href="#jucy-contact"]').hide();
	$('.jucy-submit-message').click(function(e) {
	    e.preventDefault();
	    var message = $('.jucy-contact-message').val();
	    $('.jucy-submit-message').hide();
	    $('.jucy-loader-small').show();
	    jucy_test_authentication(function() {
		$.ajax({
		    method: 'POST',
		    url: jucy_api_url + jucy_repository + '/contact/',
		    data: {
			message: message,
		    },
		    success: function(data) {
			$('#jucy-content').html(jucy_thank_you);
		    },
		    error: function(a, b, c) {
			jucy_ajax_error(a, b, c);
			$('.jucy-submit-message').show();
			$('.jucy-loader-small').hide();
		    }
		});
	    });
	    return false;
	});
    },
};

function jucy_test_authentication(callback) {
    if (jucy_authenticated_user) {
	callback();
    } else {
	$.ajax({
	    method: 'GET',
	    url: jucy_api_url + 'authenticate/',
	    success: function(data) {
		if (data['username']) {
		    jucy_authenticated_user = data;
		    callback();
		} else {
		    if (typeof jucy_current_user_email != 'undefined' && jucy_current_user_email) {
			$.ajax({
			    method: 'POST',
			    url: jucy_api_url + 'authenticate/',
			    data: {
				email: jucy_current_user_email,
				username: (typeof jucy_current_user_username != 'undefined' && jucy_current_user_username ? jucy_current_user_username : null),
			    },
			    success: function(data) {
				if (data['username']) {
				    jucy_authenticated_user = data;
				    callback();
				} else {
				    $('#jucy-content').html(data);
				    jucy_authenticate_view(callback);
				}
			    },
			    error: jucy_ajax_error,
			});
		    } else {
			$('#jucy-content').html(data);
			jucy_authenticate_view(callback);
		    }
		}
	    },
	    error: jucy_ajax_error,
	});
    }
}

function jucy_authenticate_view(callback) {
    $('.jucy-submit-email').click(function(e) {
	e.preventDefault();
	var email = $('.jucy-email-form').val();
	if (email) {
	    var data = {'email': email};
	    if ($('.jucy-password-form').length > 0) {
		data['password'] = $('.jucy-password-form').val();
	    }
	    $.ajax({
		method: 'POST',
		url: jucy_api_url + 'authenticate/',
		data: data,
		success: function(data) {
		    if (data['redirect']) {
			window.open(data['redirect'], '_blank');
		    } else if (data['username']) {
			callback();
		    } else {
			var content = $('#jucy-content');
			content.html(data);
			jucy_authenticate_view(callback);
		    }
		},
		error: jucy_ajax_error,
	    });
	}
	return false;
    });
}

function jucy_close(e) {
    if (typeof e != 'undefined') {
	e.preventDefault();
    }
    var backdrop = $('#jucy-backdrop');
    var wrapper = $('#jucy-box-wrapper');
    var jucy = $('#jucy');
    backdrop.remove();
    wrapper.remove();
    jucy.show();
    return false;
}

function jucy_external_links() {
    $('.jucy-external-link').unbind('click');
    $('.jucy-external-link').click(function(e) {
	e.preventDefault();
	window.open($(this).prop('href'), '_blank');
	return false;
    });
}

function jucy_change_tab(tab) {
    var content = $('#jucy-content');
    content.html(jucy_tabs[tab]);
    jucy_tabs_callbacks[tab]();
    jucy_external_links();
}

function jucy_show(tab) {
    var jucy = $('#jucy');
    $('body').append('<div id="jucy-backdrop"></div><div id="jucy-box-wrapper"><div id="jucy-box"><a href="#close" class="jucy-close"></a><div id="jucy-content"></div>' + jucy_footer + '</div></div>');
    jucy.hide();
    var box = $('#jucy-box');
    var wrapper = $('#jucy-box-wrapper');
    wrapper.click(jucy_close);
    box.click(function(e) { e.preventDefault(); return false; });
    $('.jucy-watermark').click(function(e) {
	window.open($(this).prop('href'), '_blank');
    });
    $('.jucy-close').click(jucy_close);
    jucy_change_tab(tab);
    $('.jucy-footer a[href^="#jucy-"]').click(function(e) {
	e.preventDefault();
	var tab = $(this).attr('href').replace('#', '');
	jucy_change_tab(tab);
	return false;
    });
}

function jucy_load() {
    if (jucy_corner_widget) {
	$('body').append('<div id="jucy" class="' + jucy_default_tab + '"></div>');
	$('#jucy').click(function(e) {
	    e.preventDefault();
	    jucy_show(jucy_default_tab);
	    return false;
	});
    }
    $('a[href="#jucy-link-ideas"]').click(function(e) { e.preventDefault(); jucy_show('jucy-ideas'); return false; });
    $('a[href="#jucy-link-help"]').click(function(e) { e.preventDefault(); jucy_show('jucy-help'); return false; });
    $('a[href="#jucy-link-contact"]').click(function(e) { e.preventDefault(); jucy_show('jucy-contact'); return false; });
    $('[data-jucy-link="ideas"]').click(function(e) { e.preventDefault(); jucy_show('jucy-ideas'); return false; });
    $('[data-jucy-link="help"]').click(function(e) { e.preventDefault(); jucy_show('jucy-help'); return false; });
    $('[data-jucy-link="contact"]').click(function(e) { e.preventDefault(); jucy_show('jucy-contact'); return false; });
}

$(document).ready(function() {
    jucy_load();
});
