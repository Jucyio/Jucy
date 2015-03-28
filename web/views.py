import github
from django.shortcuts import render
from django.conf import settings

if settings.DEBUG:
    github.enable_console_debug_logging()

class GithubWrapper(object):
    def __init__(self, request):
        self.gh = github.Github(
            login_or_token=request.user.social_auth.get().access_token,
            api_preview=True,  # so /user/repos returns repos in
                               # organizations as well.
        )

    def user(self):
        return self.gh.get_user()

    def repo(self, repo):
        return self.gh.get_repo(repo)

def index(request):
    return render(request, 'index.html', {})

def loginerror(request):
    return render(request, 'loginerror.html', {})

def pick(request):
    gh = GithubWrapper(request)
    repos = gh.user().get_repos()
    return render(request, 'pick.html', {
        'repos': repos,
    })

def board(request, full_repo_name):
    gh = GithubWrapper(request)
    issues = gh.repo(full_repo_name).get_issues()
    return render(request, 'board.html', {
        'repo': full_repo_name,
        'issues': issues,
    })

def issue(request, full_repo_name, issue_id):
    issue_id = int(issue_id)
    gh = GithubWrapper(request)
    issue = gh.repo(full_repo_name).get_issue(issue_id)
    return render(request, 'issue.html', {
        'repo': full_repo_name,
        'issue_id': issue_id,
        'issue': issue,
    })
