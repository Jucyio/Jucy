from agithub import Github
from github_mixins import GithubMixin, GithubException
import hmac
import textwrap
from django.conf import settings

assert settings.WEBHOOKS_SECRET_KEY is not None, (
    'You must set WEBHOOKS_SECRET_KEY in local_settings.py to use Jucybot')
_hmac = hmac.new(settings.WEBHOOKS_SECRET_KEY)


def get_secret_for_repo(repo):
    h = _hmac.copy()
    h.update(repo.lower())
    return h.hexdigest()


class JucyBot(GithubMixin):
    '''
    Module allowing to control the Jucybot account
    '''
    def __init__(self, gh, login):
        self.gh = gh
        self.login = login
        self.username = login
        self.label_objects = {}

    def get_webhooks_callback_url_for_repo(self, owner, repository):
        return settings.WEBHOOKS_CALLBACK_URL % {
            'owner': owner,
            'repository': repository,
            'hooktype': 'all_issues'
        }


    def setup_hooks_on_repo(self, owner, repository, gh):
        config = {
            'url': self.get_webhooks_callback_url_for_repo(owner, repository),
            'secret': get_secret_for_repo('{}/{}'.format(owner, repository)),
            'content_type': 'json',
            'secure_ssl': '1' if settings.DEBUG else '0',
        }
        try:
            hook = gh.create_hook(owner, repository, 'web', config=config,
                                    events=['issues', 'issue_comment'])
        except GithubException, e:
            pass

    def create_issue(self, owner, repository, title, contents, labels):
        body = self.format_issue(contents, labels)
        return super(JucyBot, self).create_issue(owner, repository, title, body, labels)

    def change_issue_label(self, owner, repository, issue, old_label, new_label):
       try:
           self.remove_label(owner, repository, issue, old_label)
       except GithubException, e:
           pass
       try:
           self.add_labels(owner, repository, issue, [new_label])
       except GithubException, e:
           pass

    def format_issue(self, contents, labels):
        return contents
        if not contents:
            contents = ''
        # TODO(db0): Specify the boilerplate content for Jucy issues.
        boilerplate = """*This issue was filed by Jucy*
Category: %(labels)s

%(contents_as_quote)s
"""
        contents_as_quote = textwrap.fill(contents,
                                          initial_indent='> ',
                                          subsequent_indent='> ')
        return boilerplate % {
            'labels': labels,
            'contents_as_quote': contents_as_quote,
        }

def from_github_client(gh, login=settings.JUCY_BOT_LOGIN):
    """Initializes a JucyBot instance from a Github object.

    The Github object must be authenticated as the JucyBot
    account. This can also be used to inject mock instances of the
    Github client for testing purposes.
    """
    return JucyBot(gh, login)


def from_config(login=settings.JUCY_BOT_LOGIN):
    """Initializes a JucyBot instance from the OAuth token in settings.py."""
    token = settings.JUCY_BOT_OAUTH_TOKEN
    assert token, 'JucyBot needs an OAuth token to operate.'
    gh = Github(token=token)
    return JucyBot(gh, login)
