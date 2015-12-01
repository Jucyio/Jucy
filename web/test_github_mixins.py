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
