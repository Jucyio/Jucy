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

    def repo(self, owner, repo):
        return self.gh.get_repo('%s/%s' % (owner, repo))

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

def ExtractUserRepo(path):
    segments = path.split('/')
    return segments[1], segments[2]

def ExtractUserRepoIssue(path):
    segments = path.split('/')
    return segments[1], segments[2], segments[3]

def board(request):
    boarduser, boardrepo = ExtractUserRepo(request.path)
    gh = GithubWrapper(request)
    issues = gh.repo(boarduser, boardrepo).get_issues()
    return render(request, 'board.html', {
        'boarduser': boarduser,
        'boardrepo': boardrepo,
        'issues': issues,
    })
