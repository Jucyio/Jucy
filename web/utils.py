from web import models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

def gravatar(email, size=200):
    return ("http://www.gravatar.com/avatar/"
            + hashlib.md5(email.lower()).hexdigest()
            + "?" + urllib.urlencode({'d': settings.DEFAULT_AVATAR, 's': str(size)}))

# Visitors who don't have a GitHub account can vote/comment by subscribing using
# an email address. The created users in database have this prefix to differenciate
# them from user who use their GitHub usernames.
username_prefix = 'jucyuser_'

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
    if comment.user:
        if comment.user.login == 'JucyBot':
            if command and command[0] == 'comment' and len(command) > 1:
                username = command[1]
                try:
                    user = models.User.objects.get(username=username)
                    name = user.get_full_name()
                    if not name:
                        name = user.email.split('@')[0]
                    comment.author = {
                        'username': name,
                        'avatar': gravatar(user.email),
                    }
                    return
                except ObjectDoesNotExist: pass
        else:
            comment.author = {
                'username': comment.user.name,
                'github_url': comment.user.html_url,
                'avatar': comment.user.avatar_url,
            }
            return
    comment.author = {
        'username': 'Unknown',
        'avatar': settings.DEFAULT_AVATAR,
    }

def comment_command(comment):
    """
    Will parse the comment body to see if it starts with a command.
    Returns a pair that contains the command (or None) and the modified comment.
    The returned comment will contain the right author information and a cleaned body.
    """
    comment.cleaned_body = comment.body.strip()
    command = None
    if comment.cleaned_body.startswith('@jucybot'):
        lines = comment.cleaned_body.splitlines()
        command = lines[0].split()[1:]
        if not command or not is_valid_command(command):
            command = ['comment']
        comment.cleaned_body = '\n'.join(lines[1:])
    _comment_author(comment, command)
    return comment
