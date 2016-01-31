# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render
from django.http import Http404, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from web import jucybot, models
from web.utils import get_issues_subscribers, comment_command, send_email
from web.views import ajax_authenticate, GithubWrapper
import random

def ideas_comments(request, owner, repository, full_repository_name, issue_number):
    '''
    Get the comments of an issue
    '''
    jb = jucybot.from_config()
    try:
        comments = jb.get_comments(owner, repository, issue_number)
    except exn:
        pass #FIXME
    comments = [comment_command(comment) for comment in comments]
    return render(request, 'ajax/comments.html', {
        'comments': comments,
    })

def vote_random_ideas(request, owner, repository, full_repository_name):
    """
    Get 2 random ideas
    """
    database_repository = get_object_or_404(models.Repository, owner=owner, name=repository)
    jb = jucybot.from_config()
    context = {}
    context = jb.get_issues(full_repository_name, context=context, issues_to_get=['ready'])
    # If there are not enough issues ready, also get the new issues
    if len(context['issues']) < 4:
        context = jb.get_issues(full_repository_name, context=context, issues_to_get=['new'])
    issues = get_issues_subscribers(request, database_repository, context['issues'])
    # Remove issues I already voted for
    issues = [issue for issue in issues if not issue['subscribed']]
    # If there are less than 2 issues, return null
    try:
        issues = random.sample(issues, 2)
    except ValueError:
        issues = None
    return JsonResponse({'issues': [{
        'title': issue['title'],
        'body': issue['body'],
        'number': issue['number'],
        'total_subscribers': issue['total_subscribers']
    } for issue in issues] if issues else None})

@csrf_exempt
def ideas_vote(request, owner, repository, full_repository_name, vote, issue_number):
    if not request.user.is_authenticated() or request.method != 'POST':
        raise PermissionDenied()
    repository = get_object_or_404(models.Repository, owner=owner, name=repository)
    # Get idea in database
    try:
        idea = models.Idea.objects.get(repository=repository, number=issue_number)
    except ObjectDoesNotExist:
        # Get issue on GitHub (check if it's a real one)
        jb = jucybot.from_config()
        jb.get_issue(repository.owner, repository.name, issue_number)
        idea = models.Idea.objects.create(repository=repository, number=issue_number)
    if vote == 'unvote':
        idea.subscribers.remove(request.user)
    else:
        idea.subscribers.add(request.user)
    idea.save()
    total_subscribers = idea.subscribers.all().count()
    return JsonResponse({'vote': vote, 'total_subscribers': total_subscribers})

@csrf_exempt
def authenticate(request):
    """
    GET: Will return the JSON authenticated user if any, otherwise the login HTML form.
    POST: Same, but will try to authenticate the user with the provided data.
    """
    return ajax_authenticate(request, from_api=True)

@csrf_exempt
def post_idea(request, owner, repository, full_repository_name):
    """
    Create issue using the user's account if connected with github, otherwise jucybot
    Return the issue HTML object.
    """
    if not request.user.is_authenticated() or request.method != 'POST' or 'title' not in request.POST:
        raise HttpResponseBadRequest()
    try:
        github = GithubWrapper(request)
    except ObjectDoesNotExist:
        github = jucybot.from_config()
    database_repository = get_object_or_404(models.Repository, owner=owner, name=repository)
    issue = github.create_issue(owner, repository, request.POST['title'], request.POST['content'] if 'content' in request.POST and request.POST['content'] else None, labels=['jucy'])
    idea = models.Idea.objects.create(repository=database_repository, number=issue['number'])
    idea.subscribers.add(request.user)
    idea.save()
    issue['total_subscribers'] = 1
    issue['subscribed'] = True
    return render(request, 'include/idea.html', {
        'issue': issue,
        'is_collaborator': github.is_collaborator_on_repo(owner, repository),
        'full_repository_name': full_repository_name,
    })

@csrf_exempt
def contact(request, owner, repository, full_repository_name):
    if not request.user.is_authenticated() or request.method != 'POST' or 'message' not in request.POST:
        raise HttpResponseBadRequest()
    email = models.Repository.objects.get(owner=owner, name=repository).contact_email
    send_email(subject='You got a new message from a user on Jucy 🍊', context={
        'message': request.POST['message'],
        'sender': request.user.email,
    }, template_name='contact', to=[email])
    return JsonResponse({'email': 'sent'})
