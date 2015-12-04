import copy
import github_helpers
from github_mixins import GithubException
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
        self.assertFalse(github_helpers.is_github_exception_message(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testStatusNot422(self):
        e = GithubException(404, self.hook_exists_data)
        self.assertFalse(github_helpers.is_github_exception_message(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testWorks(self):
        e = GithubException(422, self.hook_exists_data)
        self.assertTrue(github_helpers.is_github_exception_message(
            e, github_helpers.E_HOOK_ALREADY_EXISTS))

    def testBadDicts(self):
        data = copy.deepcopy(self.hook_exists_data)
        self.assertTrue(github_helpers.is_github_exception_message(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = [{u'code': u'custom', u'resource': u'Hook'}]
        self.assertFalse(github_helpers.is_github_exception_message(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = [{u'message': u'Hook already exists on this repository', u'code': u'custom', u'resource': u'Hook'}, {u'message': u'Hook already exists on this repository', u'code': u'custom', u'resource': u'Hook'}]
        self.assertFalse(github_helpers.is_github_exception_message(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        data['errors'] = []
        self.assertFalse(github_helpers.is_github_exception_message(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))
        del data['errors']
        self.assertFalse(github_helpers.is_github_exception_message(
            GithubException(422, data), github_helpers.E_HOOK_ALREADY_EXISTS))


class matchesGithubExceptionTest(unittest.TestCase):
    def makeErrorDict(self, d):
        return {
            u'documentation_url': u'https://developer.github.com/this/is/a/test',
            u'message': u'Test error',
            u'errors': [d],
        }

    def testStatus(self):
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({'a': 'b'})), {}))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(404, self.makeErrorDict({'a': 'b'})), {}))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(404, self.makeErrorDict({'a': 'b'})), {}, code=404))

    def testArray(self):
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, {}), {}))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, {u'errors': []}), {}))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, {u'errors': [{}, {}]}), {}))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, {u'errors': [{}]}), {}))

    def testDicts(self):
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({})), {}))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
            })), {}))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
            })), {
                u'foo': u'bar',
            }))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
                u'baz': u'qux',
            })), {
                u'foo': u'bar',
            }))
        self.assertTrue(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
                u'baz': u'qux',
            })), {
                u'baz': u'qux',
                u'foo': u'bar',
            }))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
            })), {
                u'foo': u'bar',
                u'baz': u'qux',
            }))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, self.makeErrorDict({
                u'foo': u'bar',
                u'baz': u'corge',
            })), {
                u'foo': u'bar',
                u'baz': u'qux',
            }))
        self.assertFalse(github_helpers.matches_github_exception(
            GithubException(422, {}), self.makeErrorDict({
                u'foo': u'bar',
                u'baz': u'qux',
            })))
