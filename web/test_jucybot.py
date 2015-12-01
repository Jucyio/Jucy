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

    def testAddAsCollaboratorOnRepo(self):
        repo = 'Jucy'
        owner = 'Jucyio'
        obj = mock.MagicMock()
        self.gh.repos[owner][repo].collaborators[self.jb.username].put.return_value = 204, obj
        self.assertEqual(self.jb.add_as_collaborator_on_repo(owner, repo), obj)
        self.gh.repos[owner][repo].collaborators[self.jb.username].put.assert_called_once_with()

    def testChangeIssueLabel(self):
        repo = mock.MagicMock()
        label1 = mock.MagicMock()
        label1.name = 'label1'
        label2 = mock.MagicMock()
        label2.name = 'label2'
        label3 = mock.MagicMock()
        label3.name = 'label3'
        issue = mock.MagicMock()
        issue.get_labels.return_value = [label1, label2]
        repo.get_labels.return_value = [label1, label2, label3]

        self.jb.change_issue_label(issue, repo, 'label3')
        issue.remove_from_labels.assert_has_calls([mock.call(label1), mock.call(label2)])
        issue.set_labels.assert_called_once_with(label3)

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
