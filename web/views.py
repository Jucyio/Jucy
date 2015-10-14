import github
import github_helpers
import jucybot
from django.shortcuts import render, redirect
from django.conf import settings

#if settings.DEBUG:
#    github.enable_console_debug_logging()

def globalContext(request):
    return {
        'debug': settings.DEBUG,
    }

class GithubWrapper(object):
    def __init__(self, request):
        if request.user.is_authenticated and not request.user.is_anonymous():
            self.gh = github.Github(
                login_or_token=request.user.social_auth.get().access_token,
                api_preview=True,  # so /user/repos returns repos in
                                   # organizations as well.
            )
        else:
            self.gh = github.Github(api_preview=True)

    def user(self):
        return self.gh.get_user()

    def repo(self, repo):
        return self.gh.get_repo(repo)

def index(request):
    context = globalContext(request)
    return render(request, 'index.html', context)

def loginerror(request):
    context = globalContext(request)
    return render(request, 'loginerror.html', context)

def pick(request):
    context = globalContext(request)
    gh = GithubWrapper(request)
    repos = gh.user().get_repos()
    context['repos'] = repos
    return render(request, 'pick.html', context)

def issue(request, full_repository_name, issue_id):
    context = globalContext(request)
    issue_id = int(issue_id)
    gh = GithubWrapper(request)
    issue = gh.repo(full_repository_name).get_issue(issue_id)
    context['repository'] = full_repository_name
    context['issue_id'] = issue_id
    context['issue'] = issue
    return render(request, 'issue.html', context)

def prepare_repo_for_jucy(request, full_repository_name):
    """Prepares a Github repo to support Jucy issues.

    This creates Jucy labels and grants Jucybot access to the
    repository.

    This function is safe to call on a repo that has already been
    initialized for Jucy. In particular, as "initializes a repo for
    Jucy" expands in scope (adding new tags, for instance), it is
    important to be able to call this function on an already partially
    initialized repo to complete the initialization. This does not
    include cleaning up leftovers from previous initialization
    scenarios: this should be done in another function.

    Args:
      request: HTTP request
      full_repo_name: name of the repo to be initialized.
    Returns:
      302 to the board for that repo.

    """
    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)

    # Step 1 : Create all the jucy labels
    for label, color in settings.JUCY_LABELS.iteritems():
        try:
            repository.create_label('%s:%s' % (settings.JUCY_LABEL_NAMESPACE, label), color)
        except github.GithubException, e:
            if not github_helpers.matchesGithubException(
                    e, {'resource': 'Label', 'code': 'already_exists'}):
                raise e

    # Step 2: grant JucyBot access to the repository
    jb = jucybot.FromConfig()
    jb.addAsCollaboratorOnRepo(repository)

    # Step 3: setup webhooks to get notifications on all issue changes
    jb.setupHooksOnRepo(repository)

    return redirect('/%s' % full_repository_name)

def ideas(request, owner, repository, full_repository_name):
    context = globalContext(request)
    gh = GithubWrapper(request)
    issues = gh.repo(full_repository_name).get_issues()
    context['repository'] = full_repository_name
    context['issues'] = issues
    context['current'] = 'ideas'
    return render(request, 'ideas.html', context)

def questions(request, owner, repository, full_repository_name):
    context = globalContext(request)
    context['current'] = 'questions'
    return render(request, 'questions.html', context)
