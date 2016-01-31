import string
import random
from web import models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Count, Q, F
from django.db.models import Prefetch
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

def send_email(subject, template_name, to=[], context={}, from_email=settings.AWS_SES_RETURN_PATH):
    context = Context(context)
    plaintext = get_template('emails/' + template_name + '.txt').render(context)
    htmly = get_template('emails/' + template_name + '.html').render(context)
    email = EmailMultiAlternatives(subject, plaintext, from_email, to)
    email.attach_alternative(htmly, "text/html")
    email.send()

def gravatar(email, size=200):
    return ("http://www.gravatar.com/avatar/"
            + hashlib.md5(email.lower()).hexdigest()
            + "?" + urllib.urlencode({'d': settings.DEFAULT_AVATAR, 's': str(size)}))

# Visitors who don't have a GitHub account can vote/comment by subscribing using
# an email address. The created users in database have this prefix to differenciate
# them from user who use their GitHub usernames.
username_prefix = 'jucyuser_'

def generate_random_username():
    return username_prefix + random_string(16)

# Commands must be on the first line of a comment.
# That line must start with @jucybot.
# This array contains: (command, minimum_arguments >=, maximum_arguments <=)
valid_commands = [
    ('comment', 0, 1), # [username of the commenter]
]

def is_valid_command(command):
    if not command:
        return False
    for (command_string, min_args, max_args) in valid_commands:
        if command_string == command[0]:
            if len(command) >= min_args and len(command) <= max_args:
                return True
            return False
    return False

def _comment_author(comment, command=None):
    if comment['user']:
        if comment['user']['login'] == 'JucyBot':
            if command and command[0] == 'comment' and len(command) > 1:
                username = command[1]
                try:
                    user = models.User.objects.get(username=username)
                    name = user.get_full_name()
                    if not name:
                        name = user.email.split('@')[0]
                    comment['author'] = {
                        'username': name,
                        'avatar': gravatar(user.email),
                    }
                    return
                except ObjectDoesNotExist: pass
        else:
            comment['author'] = {
                'username': comment['user']['login'],
                'github_url': comment['user']['html_url'],
                'avatar': comment['user']['avatar_url'],
            }
            return
    comment['author'] = {
        'username': 'Unknown',
        'avatar': settings.DEFAULT_AVATAR,
    }

def comment_command(comment):
    """
    Will parse the comment body to see if it starts with a command.
    Returns a pair that contains the command (or None) and the modified comment.
    The returned comment will contain the right author information and a cleaned body.
    """
    comment['cleaned_body'] = comment['body'].strip()
    command = None
    if comment['cleaned_body'].startswith('@jucybot'):
        lines = comment['cleaned_body'].splitlines()
        command = lines[0].split()[1:]
        if not command or not is_valid_command(command):
            command = ['comment']
        comment['cleaned_body'] = '\n'.join(lines[1:])
    _comment_author(comment, command)
    return comment

def random_string(length, choice=(string.ascii_letters + string.digits)):
    return ''.join(random.SystemRandom().choice(choice) for _ in range(length))

def is_connected_github(user):
    try:
        user.social_auth.get(provider='github')
        return True
    except ObjectDoesNotExist:
        return False

def get_issues_subscribers(request, database_repository, issues):
    """
    Takes a database repository and github issues
    Returns the issues with subscribed True/False on each and total_subscribers as an int
    """
    database_ideas = database_repository.ideas.filter(number__in=[issue['number'] for issue in issues]).annotate(total_subscribers = Count('subscribers'))
    database_ideas = database_ideas.prefetch_related(Prefetch('subscribers', queryset=models.User.objects.filter(username=request.user.username), to_attr='subscribed'))
    for issue in issues:
        issue['total_subscribers'] = 0
        issue['subscribed'] = False
        for idea in database_ideas:
            if idea.number == issue['number']:
                issue['total_subscribers'] = idea.total_subscribers
                issue['subscribed'] = bool(idea.subscribed)
    return issues
