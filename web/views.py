import github
import github_helpers
import jucybot
import forms
import labels
from django.shortcuts import render, redirect
from django.conf import settings
from mixins import GithubClientMixin

#if settings.DEBUG:
#    github.enable_console_debug_logging()

def globalContext(request):
    return {
        'debug': settings.DEBUG,
        'landing_mode': settings.LANDING_MODE,
    }

class GithubWrapper(object, GithubClientMixin):
    def __init__(self, request):
        if request.user.is_authenticated and not request.user.is_anonymous():
            self.gh = github.Github(
                login_or_token=request.user.social_auth.get().access_token,
                api_preview=True,  # so /user/repos returns repos in
                                   # organizations as well.
            )
        else:
            self.gh = github.Github(api_preview=True)
        self.label_objects = {}

def genericViewWithContext(request):
    return render(request, request.resolver_match.url_name + '.html', globalContext(request))

def pick(request):
    if settings.LANDING_MODE:
        return redirect('/_mailing')
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

def prepare_repo_for_jucy(request, owner, full_repository_name, repository):
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
    for label, color in labels.LABELS.iteritems():
        try:
            repository.create_label(label, color)
        except github.GithubException, e:
            if not github_helpers.matchesGithubException(
                    e, {'resource': 'Label', 'code': 'already_exists'}):
                raise e

    # Step 2: grant JucyBot access to the repository
    jb = jucybot.FromConfig()
    jb.add_as_collaborator_on_repo(repository)

    # Step 3: setup webhooks to get notifications on all issue changes
    jb.setup_hooks_on_repo(repository)

    return redirect('/%s' % full_repository_name)

def ideas(request, owner, repository, full_repository_name):
    context = globalContext(request)
    jb = jucybot.FromConfig()
    repository = jb.gh.get_repo(full_repository_name)
    issues = repository.get_issues()
    context['repository'] = full_repository_name
    context['issues'] = issues
    context['current'] = 'ideas'
    # Form used to create a feedback
    context['form'] = forms.FeedbackForm()
    context['request'] = request
    return render(request, 'ideas.html', context)

def questions(request, owner, repository, full_repository_name):
    context = globalContext(request)
    context['current'] = 'questions'
    return render(request, 'questions.html', context)

def create_idea(request, owner, repository, full_repository_name):
    '''
    Add a new idea, posted as the JucyBot user
    '''
    form = forms.FeedbackForm(request.POST)
    if form.is_valid():
        try:
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            jb = jucybot.from_config()
            jb.create_issue(full_repository_name, title, content, "bug")
        except github.GithubException, e:
            pass #FIXME
    return redirect('/%s' % full_repository_name)

def reject_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Reject an idea: close the issue, redirect to the ideas page
    '''
    context = globalContext(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    issue.edit(state="closed")

    issues = repository.get_issues()
    context['repository'] = full_repository_name
    context['issues'] = issues
    context['current'] = 'ideas'
    return render(request, 'ideas.html', context)

def approve_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Approve an idea: Label the issue as ready
    '''
    context = globalContext(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    labels = repository.get_labels()
    ready_label = next((label for label in labels if label.name == "ready"), None)
    issue.set_labels(ready_label)

    issues = repository.get_issues()
    context['repository'] = full_repository_name
    context['issues'] = issues
    context['current'] = 'ideas'
    return render(request, 'ideas.html', context)

def duplicate_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Mark an idea as duplicate: close the issue, add duplicate label, redirect to the ideas page
    '''
    context = globalContext(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    issue.edit(state="closed", labels=["duplicate"])

    issues = repository.get_issues()
    context['repository'] = full_repository_name
    context['issues'] = issues
    context['current'] = 'ideas'
    return render(request, 'ideas.html', context)
