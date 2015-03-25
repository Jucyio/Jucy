import agithub
from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})

def loginerror(request):
    return render(request, 'loginerror.html', {})

def pick(request):
    tok = request.user.social_auth.get().access_token
    gh = agithub.Github(token=tok)
    gh.setConnectionProperties(agithub.ConnectionProperties(
        extra_headers={
        'accept': 'application/vnd.github.moondragon+json',
        },
        secure_http=True,
        api_url='api.github.com'))
    repos = gh.user.repos.get()
    return render(request, 'pick.html', {'repos': repos})
