import github
import github_helpers
import jucybot
import forms
import labels
from django.shortcuts import render, redirect
from django.conf import settings

#if settings.DEBUG:
#    github.enable_console_debug_logging()

def global_context(request):
    return {
        'debug': settings.DEBUG,
        'landing_mode': settings.LANDING_MODE,
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
        self.label_objects = {}

    def user(self):
        return self.gh.get_user()

    def repo(self, repo):
        return self.gh.get_repo(repo)

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
    context = global_context(request)
    context['repos'] = ['Asteks/Moulinettes','Asteks/poolTek0','db0company/AndroidReviews','db0company/API.swift','db0company/cha.moe','db0company/Chrono.db0','db0company/Copliator','db0company/css-hexagon','db0company/CuteForm','db0company/db0.fr','db0company/django-media-manager','db0company/ExSwift','db0company/FFmpeg','db0company/ffmpeg-web','db0company/Gallery','db0company/GCal','db0company/generic-api','db0company/GitHub-API-OCaml','db0company/HenTie','db0company/Ionis-Users-Informations','db0company/Ionis-Users-Informations-Web-Service','db0company/itoa','db0company/itunes-iap','db0company/Konami','db0company/Lambda-calcul_eval_AST','db0company/linguist','db0company/List','db0company/lolicri.es','db0company/Meow','db0company/MyAnimeList-pictures','db0company/navbar-variant','db0company/Ocsigen-Quick-Howto','db0company/OcsiTools','db0company/PaginatedTableView','db0company/Pathname','db0company/paysdu42','db0company/R-Type','db0company/Radio.db0','db0company/s3_bucket_to_bucket_copy_py','db0company/Social-Bar','db0company/UCBerkeley-cs61c','db0company/UCBerkeley-cs61c-Project2','db0company/Zappy','db0company/Zero-Fansub-website','db0company/Zia','gilfein/YESorNO','gilfein/YESorNO-API','LamaUrbain/Experimentations','LamaUrbain/LamaFetcher','LamaUrbain/LamaMobile','LamaUrbain/LamaServer','LamaUrbain/LamaVitrine','LamaUrbain/LamaWeb','LamaUrbain/libosmscout','LamaUrbain/ocaml-gpx','LamaUrbain/ocaml-memphis','LamaUrbain/Tasks','Lateb/dtc.lateb.org','Lateb/Epicard','Lateb/fortune','Lateb/www','Life-the-game/APInode','Life-the-game/APIpy','Life-the-game/Applications','Life-the-game/django-ios-notifications','Life-the-game/HappyPie','Life-the-game/iOs','Life-the-game/Missions','Life-the-game/Open-Discussions','Life-the-game/Portal','Life-the-game/Preview','Life-the-game/Scripts','Life-the-game/SDK-JQuery','Life-the-game/SDK-OCaml','Life-the-game/SDK-PHP','Life-the-game/Showcase','Life-the-game/Tasks','Life-the-game/Website','mindie/Mindie-WWW','ReturnToLife/BiblioTECH','ReturnToLife/Dev','ReturnToLife/Pi-E','ReturnToLife/Portal2','ReturnToLife/Portal3','ReturnToLife/Portal4','ReturnToLife/Portal4_API','ReturnToLife/Portal5','ReturnToLife/Portal5_API','rFlex/YESorNO-API','SchoolIdolTomodachi/frgl','SchoolIdolTomodachi/SchoolIdolAPI','SchoolIdolTomodachi/SchoolIdolContest','SchoolIdolTomodachi/Sukutomo-Android','SchoolIdolTomodachi/Sukutomo-iOs','Solvik/Zappy','unitech-io/EChat','unitech-io/ESchool','unitech-io/Nurse-api-sandbox','unitech-io/p3ee-blog-theme','unitech-io/Quizzy',]
    # gh = GithubWrapper(request)
    # repos = gh.user().get_repos()
    # context['repos'] = repos
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
    repository = gh.repo(full_repository_name)
    # Step 1 : Create all the jucy labels
    for label, color in labels.LABELS.iteritems():
        try:
            repository.create_label(label, color)
        except github.GithubException, exn:
            if not github_helpers.matchesGithubException(
                    exn, {'resource': 'Label', 'code': 'already_exists'}):
                raise exn

    # Step 2: grant JucyBot access to the repository
    jb = jucybot.from_config()

    jb.add_as_collaborator_on_repo(repository)

    # Step 3: setup webhooks to get notifications on all issue changes
    jb.setup_hooks_on_repo(repository)

    return redirect('/%s' % full_repository_name)

def prepare_issues_context(context, full_repository_name, repository, current_view):
    try:
        issues = repository.get_issues()
        context['issues'] = issues
    except github.GithubException, exn:
        pass #FIXME
    context['repository'] = full_repository_name
    context['current'] = current_view

def ideas(request, owner, repository, full_repository_name):
    context = global_context(request)
    jb = jucybot.from_config()
    repository = jb.gh.get_repo(full_repository_name)
    prepare_issues_context(context, full_repository_name, repository, 'ideas')
    # Form used to create a feedback
    context['form'] = forms.FeedbackForm()
    context['request'] = request
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

def reject_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Reject an idea: close the issue, redirect to the ideas page
    '''
    context = global_context(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    issue.edit(state="closed")

    prepare_issues_context(context, full_repository_name, repository, 'ideas')
    return render(request, 'ideas.html', context)

def approve_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Approve an idea: Label the issue as ready
    '''
    context = global_context(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    labels = repository.get_labels()
    ready_label = next((label for label in labels if label.name == "ready"), None)
    issue.set_labels(ready_label)

    prepare_issues_context(context, full_repository_name, repository, 'ideas')
    return render(request, 'ideas.html', context)

def duplicate_idea(request, owner, repository, full_repository_name, issue_id):
    '''
    Mark an idea as duplicate: close the issue, add duplicate label, redirect to the ideas page
    '''
    context = global_context(request)

    gh = GithubWrapper(request)
    repository = gh.repo(full_repository_name)
    issue_id = int(issue_id)
    issue = repository.get_issue(issue_id)
    issue.edit(state="closed", labels=["duplicate"])

    prepare_issues_context(context, full_repository_name, repository, 'ideas')
    return render(request, 'ideas.html', context)
