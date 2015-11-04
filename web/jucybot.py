import github
import github_helpers
import hmac
import textwrap
from django.conf import settings
from mixins import GithubClientMixin

assert settings.WEBHOOKS_SECRET_KEY is not None, (
    'You must set WEBHOOKS_SECRET_KEY in local_settings.py to use Jucybot')
_hmac = hmac.new(settings.WEBHOOKS_SECRET_KEY)


def getSecretForRepo(repo):
    h = _hmac.copy()
    h.update(repo.lower())
    return h.hexdigest()


class JucyBot(object, GithubClientMixin):
    def __init__(self, gh, login):
        self.gh = gh
        self.login = login
        self.label_objects = {}

    def get_webhooks_callback_url_for_repo(self, repo):
        return settings.WEBHOOKS_CALLBACK_URL % {
            'owner': repo.owner.login,
            'repository': repo.name,
            'hooktype': 'all_issues'
        }

    def setup_hooks_on_repo(self, repo):
        config = {
            'url': self.getWebhooksCallbackUrlForRepo(repo),
            'secret': getSecretForRepo(repo.full_name),
            'content_type': 'json',
            'secure_ssl': '1' if settings.DEBUG else '0',
        }
        try:
            hook = repo.create_hook('web', config,
                                    events=['issues', 'issue_comment'])
            return True
        except github.GithubException, e:
            if github_helpers.isGithubExceptionMessage(
                    e, github_helpers.E_HOOK_ALREADY_EXISTS):
                return True
            raise e


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
    gh = github.Github(token)
    return JucyBot(gh, login)
