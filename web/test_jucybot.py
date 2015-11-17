import github
import jucybot
import unittest
import mock
from django.test.utils import override_settings
from django.test import TestCase


class JucyBotTest(unittest.TestCase):
    def setUp(self):
        self.gh = mock.MagicMock()
        self.jb = jucybot.from_github_client(self.gh, login='testJucyBot')

    def testFormatIssue(self):
        expected = """*This issue was filed by Jucy*
Category: feedback

> This website is great!
"""
        self.assertEqual(expected,
                         self.jb.format_issue('This website is great!',
                                             'feedback'))

    def testCreateIssue(self):
        repo_obj = mock.MagicMock()
        label_obj = mock.MagicMock()
        repo_obj.get_label.return_value = label_obj
        self.gh.repo.return_value = repo_obj

        title = 'Test issue'
        contents = 'This website is great!'
        self.jb.create_issue('Jucyio/playground', title, contents, 'feedback')

        self.gh.repo.assert_called_with('Jucyio/playground')
        repo_obj.get_label.assert_called_with('feedback')
        repo_obj.create_issue.assert_called_with(title,
                                                 body=mock.ANY,
                                                 labels=[label_obj])

    def testIsCollaboratorOnRepo(self):
        repo = mock.MagicMock()
        repo.has_in_collaborators.return_value = True
        self.assertTrue(self.jb.is_collaborator_on_repo(repo))
        repo.has_in_collaborators.assert_called_once_with('testJucyBot')
        repo = mock.MagicMock()
        repo.has_in_collaborators.return_value = False
        self.assertFalse(self.jb.is_collaborator_on_repo(repo))
        repo.has_in_collaborators.assert_called_once_with('testJucyBot')

    def testAddAsCollaboratorOnRepo(self):
        repo = mock.MagicMock()
        self.jb.add_as_collaborator_on_repo(repo)
        repo.add_to_collaborators.assert_called_once_with('testJucyBot')


@override_settings(PER_REPO_WEBHOOK_KEY='testkey1')
class PerRepoSecretTest(TestCase):

    def testIsIdempotent(self):
        key1 = jucybot.get_secret_for_repo('Jucyio/Jucy')
        key2 = jucybot.get_secret_for_repo('Megacorp/SuperSecretProject')
        key3 = jucybot.get_secret_for_repo('Megacorp/SuperSecretProject')
        key4 = jucybot.get_secret_for_repo('Jucyio/Jucy')
        self.assertTrue(key1)
        self.assertEqual(key1, key4)
        self.assertEqual(key2, key3)
        self.assertNotEqual(key1, key2)

    def testIsCaseInsensitive(self):
        key1 = jucybot.get_secret_for_repo('Jucyio/Jucy')
        key2 = jucybot.get_secret_for_repo('jucyio/jucy')
        self.assertEqual(key1, key2)
