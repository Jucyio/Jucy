import copy
import github_helpers
from github import GithubException
import unittest

class isGithubExceptionMessageTest(unittest.TestCase):
    hook_exists_data = {
        u'documentation_url': u'https://developer.github.com/v3/repos/hooks/#create-a-hook',
        u'message': u'Validation Failed',
        u'errors': [
            {
                u'message': u'Hook already exists on this repository',
                u'code': u'custom',
                u'resource': u'Hook'
            }
        ]
    }

    def testStatusNotError(self):
        e = GithubException(200, self.hook_exists_data)
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testStatusNot422(self):
        e = GithubException(404, self.hook_exists_data)
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testWorks(self):
        e = GithubException(422, self.hook_exists_data)
        self.assertTrue(github_helpers.isGithubExceptionMessage(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testBadDicts(self):
        data = copy.deepcopy(self.hook_exists_data)
        self.assertTrue(github_helpers.isGithubExceptionMessage(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = [{u'code': u'custom', u'resource': u'Hook'}]
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = [{u'message': u'Hook already exists on this repository', u'code': u'custom', u'resource': u'Hook'}, {u'message': u'Hook already exists on this repository', u'code': u'custom', u'resource': u'Hook'}]
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = []
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        del data['errors']
        self.assertFalse(github_helpers.isGithubExceptionMessage(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
