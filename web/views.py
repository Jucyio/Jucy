from agithub import Github
from github_mixins import GithubMixin, GithubException
import github_helpers
import jucybot
import forms
import labels
import models
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import resolve
from django.conf import settings
from web.utils import *

#if settings.DEBUG:
#    github.enable_console_debug_logging()

def global_context(request):
    return {
        'debug': settings.DEBUG,
        'landing_mode': settings.LANDING_MODE,
        'current': resolve(request.path_info).url_name,
    }

class GithubWrapper(GithubMixin):
    def __init__(self, request):
        if request.user.is_authenticated and not request.user.is_anonymous():
            self.username = request.user.username
            self.gh = Github(token=request.user.social_auth.get().access_token)
        else:
            self.gh = Github()
        self.label_objects = {}

def genericViewWithContext(request):
    return render(request, request.resolver_match.url_name + '.html', global_context(request))

def index(request):
    context = global_context(request)
    return render(request, 'index.html', context)

def loginerror(request):
    context = global_context(request)
    return render(request, 'loginerror.html', context)

def pick(request):
    if settings.LANDING_MODE:
        return redirect('/_mailing')
    if 'repository' in request.POST:
        return redirect('/' + request.POST['repository'])
    if not request.user.is_authenticated and request.user.is_anonymous():
        return login_error

    context = global_context(request)
    jb = jucybot.from_config()
    user_repos = jb.get_user_repos(request.user.username)
    jucy_repos = jb.get_repos()

    jucy_set = set(repo['full_name'] for repo in jucy_repos)
    user_set = set(repo['full_name'] for repo in user_repos)
    context['repos'] = list(user_set & jucy_set)
    return render(request, 'pick.html', context)

def issue(request, full_repository_name, issue_id):
    context = global_context(request)
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

    # Step 1 : Create all the jucy labels
    for label, color in labels.LABELS.iteritems():
        try:
            gh.create_label(owner, repository, label, color)
        except GithubException, exn:
            if not github_helpers.matches_github_exception(
                            exn, {'resource': 'Label', 'code': 'already_exists'}):
                raise exn

    # Step 2: grant JucyBot access to the repository
    jb = jucybot.from_config()

    jb.add_as_collaborator_on_repo(owner, repository)

    # Step 3: setup webhooks to get notifications on all issue changes
    jb.setup_hooks_on_repo(owner, repository, gh)

    # Step 4: create a Repo object and save it
    repo_model, _ =  models.Repo.objects.get_or_create(name=repository, owner=owner)
    repo_model.save()
    return redirect('/%s' % full_repository_name)


def prepare_issues_context(context, jb, full_repository_name, repository, current_view):
    try:
        jb.get_issues(full_repository_name, context=context)
    except GithubException, exn:
        pass #FIXME
    context['repository'] = full_repository_name
    context['current'] = current_view

def ideas(request, owner, repository, full_repository_name):
    context = global_context(request)
    jb = jucybot.from_config()

    context['is_collaborator'] = False
    if request.user.is_authenticated():
        gh = GithubWrapper(request)
        if gh.is_collaborator_on_repo(owner, repository):
            context['is_collaborator'] = True

    prepare_issues_context(context, jb, full_repository_name, repository, 'ideas')
    if context['is_collaborator']:
        context['issues'] = context['new']['items'] + context['ready']['items']
    else:
        context['issues'] = context['ready']['items']

    context['request'] = request
    context['full_repository_name'] = full_repository_name
    return render(request, 'ideas.html', context)

def questions(request, owner, repository, full_repository_name):
    context = global_context(request)
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

def get_issue_comments(request, owner, repository, full_repository_name, issue_id):
    '''
    Get the comments of an issue
    '''
    gh = GithubWrapper(request)
    issue_id = int(issue_id)
    try:
        comments = gh.get_comments(owner, repository, issue_id)
    except exn:
        pass #FIXME
    comments = [comment_command(comment) for comment in comments]
    return render(request, 'ajax/comments.html', {
        'comments': comments,
    })
    # comments = {'comments': [{
    #     'body': comment.body,
    #     'user': None if not comment.user or comment.user.login == 'jucybot' else {
    #         'avatar': comment.user.avatar_url,
    #         'login': comment.user.login,
    #     },
    # } for comment in comments]}
    return JsonResponse(json_comments)
