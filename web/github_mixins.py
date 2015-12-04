import json

class GithubException(Exception):
    def __init__(self, status_code, data):
        self.data = data
        self.status = status_code

    def __str__(self):
        return json.dumps(self.data)

class GithubMixin(object):

    def _wrap_error(self, expected_status, status_code, data):
        """ Wraps Github API errors

        Args:
            expected_status (int): HTTP status code expected for the reply
            data (dict): The data returned by the request

        Function will raise a GithubException if the status_code isn't the same as expected

        """
        if status_code != expected_status:
            raise GithubException(status_code, data)
        return data

    def get_repos(self, *args, **kwargs):
        """ Return all repositories available to the user

        Github Reference:
            path: /user/repos/
            method: GET
            reference: https://developer.github.com/v3/repos/#list-your-repositories

        Args:
            *args and **kwargs are passed as GET parameter to the request constructor
            see available parameters in the Github API reference

        """
        status_code, data = self.gh.user.repos.get(*args, **kwargs)
        return self._wrap_error(200, status_code, data)

    def get_user_repos(self, username):
        """ Return all repositories available to the specified user

        Github Reference:
            path: /users/:username/repos
            method: GET
            reference: https://developer.github.com/v3/repos/#list-user-repositories

        Args:
            username (str) : Github username

        """
        status_code, data = self.gh.users[username].repos.get()
        return self._wrap_error(200, status_code, data)

    def repo(self, username, repo):
        """ Return a repository

        Github Reference:
            path: /repos/:owner/:repo
            method: GET
            reference: https://developer.github.com/v3/repos/#get

        Args:
            username (str) : Github username
            repo (str) : Github repository name

        """
        status_code, data = self.gh.repos[username][repo].get()
        return self._wrap_error(200, status_code, data)

    def is_collaborator_on_repo(self, owner, repo):
        """ Return True is the user is collaborator for the specified repository, else False.

        Github Reference:
            path: /repos/:owner/:repo/collaborators/:username
            method: GET
            reference: https://developer.github.com/v3/repos/collaborators/#check-if-a-user-is-a-collaborator

        Args:
            owner (str) : Github username
            repo (str) : Github repository name

        """
        status_code, data = self.gh.repos[owner][repo].collaborators[self.username].get()
        if status_code == 404:
            return False
        elif status_code == 204:
            return True
        else:
            raise GithubException(data)

    def search_issues(self, *args, **kwargs):
        """ Do an issue search

        Github Reference:
            path: /search/issues
            method: GET
            reference: https://developer.github.com/v3/search/#search-issues

        Args:
            **kwargs are passed as search pattern according to the q syntax specified in the API reference.
            For example, search_issues(state='open', label='bug') will search with q=state:open label:bug.
            Negation for a pattern can be obtained by prefixing a value with '-':
            Example: search_issues(label='-bug') will search with q=-label:bug

        """
        q = ''
        for key, value in kwargs.iteritems():
            if value.startswith('-'):
                q += ' -{}:{}'.format(key, value[1:])
            else:
                q += ' {}:{}'.format(key, value)
        status_code, data = self.gh.search.issues.get(q=q)
        return self._wrap_error(200, status_code, data)

    def get_issues(self, full_repository_name, context=None):
        """ Return issues for the given repository.

        Args:
            full_repository_name (str) :  Github repository full name
            context (dict) : A dictionnary that will be updated with the issues retrieved.

        It will split the result in a dictionnary, according to the following principles:

        - If an issue is closed, and the duplicate label is set: 'duplicate'
        - If an issue is closed, and the rejected label is set: 'rejected'
        - If an issue is closed without the aforementioned labels: 'done'
        - If an issue is open, with a ready label set: 'ready'
        - If an issue is open without the ready label: 'new'

        If a context object is given, it will populate it, else it will return a n-uple:
        (new, ready, duplicated, done, rejected)

        """

        duplicates = self.search_issues(repo=full_repository_name, state='closed', label='duplicate')
        rejected = self.search_issues(repo=full_repository_name, state='closed', label='rejected')
        done = self.search_issues(repo=full_repository_name, state='closed', labels='-rejected,duplicate')
        ready = self.search_issues(repo=full_repository_name, state='open', label='ready')
        new = self.search_issues(repo=full_repository_name, state='open', label='-ready')

        if context:
            context['new'] = new
            context['ready'] = ready
            context['duplicates'] = duplicates
            context['done'] = done
            context['rejected'] = rejected
        else:
            return (new, ready, duplicates, done, rejected)

    def get_comments(self, owner, repository, issue):
        """ Return comments for a given issue

        Github Reference:
            path: /repos/:owner/:repo/issues/:number/comments
            method: GET
            reference: https://developer.github.com/v3/repos/comments/#list-commit-comments-for-a-repository

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            issue (int) : Issue id

        """
        status_code, data = self.gh.repos[owner][repository].issues[str(issue)].comments.get()
        return self._wrap_error(200, status_code, data)

    def create_hook(self, owner, repository, name, config, events):
        """ Create a hook for the given repository

        Github Reference:
            path: /repos/:owner/:repo/hooks
            method: POST
            reference: https://developer.github.com/v3/repos/hooks/#create-a-hook

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            name (str) : Webhook name
            config (dict) : config object as specified in the Github API reference
            events (list) : events to register to as specified in the Github API reference

        """
        payload = {'config': config, 'events': events, 'name': name}
        status_code, data = self.gh.repos[owner][repository].hooks.post(body=payload)
        return self._wrap_error(201, status_code, data)

    def create_label(self, owner, repository, name, color):
        """ Create a new label

        Github Reference:
            path: /repos/:owner/:repo/labels
            method: POST
            reference: https://developer.github.com/v3/issues/labels/#create-a-label

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            name (str) : Label name
            color (str) : Label color

        """
        payload = {'name': name, 'color': color}
        status_code, data = self.gh.repos[owner][repository].labels.post(body=payload)
        return self._wrap_error(201, status_code, data)

    def create_issue(self, owner, repository, title, content, labels):
        """ Create an issue

        Github Reference:
            path: /repos/:owner/:repo/issues
            method: POST
            reference: https://developer.github.com/v3/issues/#create-an-issue

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            title (str) : Issue title
            content (str) : Issue body
            label : Issue label

        """
        payload = {'title': title, 'body': content, 'labels': labels}
        status_code, data = self.gh.repos[owner][repository].issues.post(body=payload)
        return self._wrap_error(201, status_code, data)

    def remove_label(self, owner, repository, issue, label):
        """ Remove a label from an issue

        Github Reference:
            path: /repos/:owner/:repo/issues/:number/labels/:name
            method: DELETE
            reference: https://developer.github.com/v3/issues/labels/#remove-a-label-from-an-issue

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            issue (int) : Issue id
            label (str) : Label

        """
        status_code, data = self.gh.repos[owner][repository].issues[str(issue)].labels[label].delete()
        return self._wrap_error(200, status_code, data)

    def replace_labels(self, owner, repository, issue, labels):
        """ Replace labels from an issue

        Github Reference:
            path: /repos/:owner/:repo/issues/:number/labels
            method: PUT
            reference: https://developer.github.com/v3/issues/labels/#replace-all-labels-for-an-issue

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            issue (int) : Issue id
            labels (str list) : Labels

        """
        status_code, data = self.gh.repos[owner][repository].issues[str(issue)].labels.put(body=labels)
        return self._wrap_error(200, status_code, data)

    def get_issue(self, owner, repository, issue):
        """ get a single issue

        github reference:
            path: /repos/:owner/:repo/issues/:number
            method: GET
            reference: https://developer.github.com/v3/issues/#get-a-single-issue

        args:
            owner (str) : github username
            repository (str) : github repository
            issue (int) : issue id

        """
        status_code, data = self.gh.repos[owner][repository].issues[str(issue)].get()
        return self._wrap_error(200, status_code, data)

    def add_labels(self, owner, repository, issue, labels):
        """ Add labels to an issue

        Github Reference:
            path: /repos/:owner/:repo/issues/:number/labels
            method: POST
            reference: https://developer.github.com/v3/issues/labels/#replace-all-labels-for-an-issue

        Args:
            owner (str) : Github username
            repository (str) : Github repository
            issue (int) : Issue id
            labels (str list) : Labels

        """
        status_code, data = self.gh.repos[owner][repository].issues[str(issue)].labels.post(body=labels)
        return self._wrap_error(200, status_code, data)
