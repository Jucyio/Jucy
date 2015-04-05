import github
import github_helpers
import hmac
import textwrap
from django.conf import settings

assert settings.WEBHOOKS_SECRET_KEY is not None, (
    'You must set WEBHOOKS_SECRET_KEY in local_settings.py to use Jucybot')
_hmac = hmac.new(settings.WEBHOOKS_SECRET_KEY)


def getSecretForRepo(repo):
    h = _hmac.copy()
    h.update(repo.lower())
    return h.hexdigest()


class JucyBot(object):
    def __init__(self, gh, login):
        self.gh = gh
        self.login = login
        self.label_objects = {}

    def isCollaboratorOnRepo(self, repo):
        return repo.has_in_collaborators(self.login)

    def addAsCollaboratorOnRepo(self, repo):
        repo.add_to_collaborators(self.login)

    def getLabelObject(self, repo, label_name):
        key = (repo.full_name, label_name)
        if key in self.label_objects:
            return self.label_objects[key]
        label = repo.get_label(label_name)
        self.label_objects[key] = label
        return label

    def formatIssue(self, contents, label_name):
        # TODO(db0): Specify the boilerplate content for Jucy issues.
        boilerplate = """*This issue was filed by Jucy*
Category: %(label_name)s

%(contents_as_quote)s
"""
        contents_as_quote = textwrap.fill(contents,
                                          initial_indent='> ',
                                          subsequent_indent='> ')
        return boilerplate % {
            'label_name': label_name,
            'contents_as_quote': contents_as_quote,
        }

    def createIssue(self, repo_fullname, title, contents, label_name):
        body = self.formatIssue(contents, label_name)
        repo = self.gh.repo(repo_fullname)
        return repo.create_issue(
            title,
            body=body,
            labels=[self.getLabelObject(repo, label_name)])

    def getWebhooksCallbackUrlForRepo(self, repo):
        return settings.WEBHOOKS_CALLBACK_URL % {
            'owner': repo.owner.login,
            'repository': repo.name,
            'hooktype': 'all_issues'
        }

    def setupHooksOnRepo(self, repo):
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


def FromGithubClient(gh, login=settings.JUCY_BOT_LOGIN):
    """Initializes a JucyBot instance from a Github object.

    The Github object must be authenticated as the JucyBot
    account. This can also be used to inject mock instances of the
    Github client for testing purposes.
    """
    return JucyBot(gh, login)


def FromConfig(login=settings.JUCY_BOT_LOGIN):
    """Initializes a JucyBot instance from the OAuth token in settings.py."""
    token = settings.JUCY_BOT_OAUTH_TOKEN
    assert token, 'JucyBot needs an OAuth token to operate.'
    gh = github.Github(token)
    return JucyBot(gh, login)
