from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound

def handle_ping(request, repo):
    return HttpResponse()

def handle_issues(request, repo):
    return HttpResponse()

def handle_issue_comment(request, repo):
    return HttpResponse()

def dispatch(request, repo, hook):
    github_event = request.META.get('HTTP_X_GITHUB_EVENT')
    if not github_event:
        return HttpResponseNotFound('No X-GitHub-Event!')
    if github_event == 'ping':
        return handle_ping(request, repo)
    elif github_event == 'issue_comment':
        return handle_issue_comment(request, repo)
    elif github_event == 'issues':
        return handle_issues(request, repo)
    else:
        return HttpResponseNotFound('Unknown event!')

@csrf_exempt
def all_issues(request, full_repo_name):
    return dispatch(request, repo=full_repo_name, hook='all_issues')
