import unittest
import mock
from django.test.utils import override_settings
from django.test import TestCase
from github_mixins import GithubMixin, GithubException

class TestClient(GithubMixin):
    def __init__(self, username, gh):
        self.username = username
        self.gh = gh

class GithubMixinTest(unittest.TestCase):
    def setUp(self):
        self.gh = mock.MagicMock()
        self.client = TestClient('Jucybot', self.gh)

    def testWrapError(self):
        status_code = 201
        data_obj = mock.MagicMock()

        with self.assertRaises(GithubException):
            self.client._wrap_error(404, status_code, data_obj)

    def testGetRepos(self):
        repos = mock.MagicMock()
        self.gh.user.repos.get.return_value = 200, repos
        self.assertEqual(self.client.get_repos(), repos)

        with self.assertRaises(GithubException):
            self.gh.user.repos.get.return_value = 404, repos
            self.client.get_repos()

    def testGetUserRepos(self):
        repos = mock.MagicMock()
        username = 'Jucybot'
        self.gh.users[username].repos.get.return_value = 200, repos
        self.assertEqual(self.client.get_user_repos(username), repos)
        self.gh.users[username].repos.get.assert_called_with()

    def testRepo(self):
        username = 'Jucybot'
        repo = 'Jucy'
        repo_obj = mock.MagicMock()
        self.gh.repos[username][repo].get.return_value = 200, repo_obj
        self.assertEqual(self.client.repo(username, repo), repo_obj)

    def testIsCollaboratorOnRepo(self):
        owner = 'Jucyio'
        repo = 'Jucy'
        self.gh.repos[owner][repo].collaborators[self.client.username].get.return_value = 404, None
        self.assertFalse(self.client.is_collaborator_on_repo(owner, repo))
        self.gh.repos[owner][repo].collaborators[self.client.username].get.return_value = 204, None
        self.assertTrue(self.client.is_collaborator_on_repo(owner, repo))

    def testSearchIssue(self):
        kwargs = {'label':'bug', 'state':'-closed'}
        expected_query = ' -state:closed label:bug'
        search_result = mock.MagicMock()
        self.gh.search.issues.get.return_value = 200, search_result
        self.assertEqual(self.client.search_issues(**kwargs), search_result)
        self.gh.search.issues.get.assert_called_with(q=expected_query)

    def testGetIssues(self):
        repository = 'Jucyio/Jucy'
        duplicates_query = ' repo:Jucyio/Jucy state:closed label:duplicate'
        rejected_query = ' repo:Jucyio/Jucy state:closed label:rejected'
        ready_query = ' repo:Jucyio/Jucy state:open label:ready'
        done_query = ' repo:Jucyio/Jucy state:closed -labels:rejected,duplicate'
        new_query = ' repo:Jucyio/Jucy state:open -label:ready'
        search_result = mock.MagicMock()
        self.gh.search.issues.get.return_value = 200, search_result

        self.client.get_issues(repository)
        self.gh.search.issues.get.assert_any_call(q=rejected_query)
        self.gh.search.issues.get.assert_any_call(q=ready_query)
        self.gh.search.issues.get.assert_any_call(q=duplicates_query)
        self.gh.search.issues.get.assert_any_call(q=new_query)
        self.gh.search.issues.get.assert_any_call(q=done_query)

    def testGetComments(self):
        owner = 'Jucyio'
        repo = 'Jucy'
        issue = 1
        comments_obj = mock.MagicMock()
        self.gh.repos[owner][repo].issues[str(issue)].comments.get.return_value = 200, comments_obj
        self.assertEqual(self.client.get_comments(owner, repo, 1), comments_obj)

    def testCreateHook(self):
        owner = 'Jucyio'
        repo = 'Jucy'
        name = 'web'
        config = mock.MagicMock()
        events = mock.MagicMock()
        hook_obj = mock.MagicMock()

        payload = {'config': config, 'events': events, 'name': name}
        self.gh.repos[owner][repo].hooks.post.return_value = 201, hook_obj
        self.assertEqual(self.client.create_hook(owner, repo, name, config, events), hook_obj)
        self.gh.repos[owner][repo].hooks.post.assert_called_with(body=payload)

    def testCreateLabel(self):
        owner = 'Jucyio'
        repo = 'Jucy'
        name = 'bug'
        color = 'ffffff'
        payload = {'name': name, 'color': color}
        label_obj = mock.MagicMock()

        self.gh.repos[owner][repo].labels.post.return_value = 201, label_obj
        self.assertEqual(self.client.create_label(owner, repo, name, color), label_obj)
        self.gh.repos[owner][repo].labels.post.assert_called_with(body=payload)

    def testCreateIssue(self):
        owner = 'Jucyio'
        repo = 'Jucy'
        title = 'Issue'
        content = 'Hello'
        labels = mock.MagicMock()
        issue = mock.MagicMock()
        payload = {'title': title, 'body': content, 'labels': labels}

        self.gh.repos[owner][repo].issues.post.return_value = 201, issue
        self.assertEqual(self.client.create_issue(owner, repo, title, content, labels), issue)
        self.gh.repos[owner][repo].issues.post.assert_called_once_with(body=payload)

    def testAddAsCollaboratorOnRepo(self):
        repo = 'Jucy'
        owner = 'Jucyio'
        username = 'toto'
        obj = mock.MagicMock()
        self.gh.repos[owner][repo].collaborators[username].put.return_value = 204, obj
        self.assertEqual(self.client.add_as_collaborator_on_repo(owner, repo, username), obj)
        self.gh.repos[owner][repo].collaborators[username].put.assert_called_once_with()
