import github
import jucybot
import unittest
import mock

class JucyBotTest(unittest.TestCase):
    def setUp(self):
        self.gh = mock.MagicMock()
        self.jb = jucybot.FromGithubClient(self.gh, login='testJucyBot')

    def testFormatIssue(self):
        expected = """*This issue was filed by Jucy*
Category: feedback

> This website is great!
"""
        self.assertEqual(expected, self.jb.formatIssue(
            'This website is great!', 'feedback'))

    def testCreateIssue(self):
        repo_obj = mock.MagicMock()
        label_obj = mock.MagicMock()
        repo_obj.get_label.return_value = label_obj
        self.gh.repo.return_value = repo_obj

        title = 'Test issue'
        contents = 'This website is great!'
        self.jb.createIssue(
            'Jucyio/playground', title, contents, 'feedback')

        self.gh.repo.assert_called_with('Jucyio/playground')
        repo_obj.get_label.assert_called_with('feedback')
        repo_obj.create_issue.assert_called_with(title, body=mock.ANY, labels=[label_obj])

    def testIsCollaboratorOnRepo(self):
        repo = mock.MagicMock()
        repo.has_in_collaborators.return_value = True
        self.assertTrue(self.jb.isCollaboratorOnRepo(repo))
        repo.has_in_collaborators.assert_called_once_with('testJucyBot')
        repo = mock.MagicMock()
        repo.has_in_collaborators.return_value = False
        self.assertFalse(self.jb.isCollaboratorOnRepo(repo))
        repo.has_in_collaborators.assert_called_once_with('testJucyBot')

    def testAddAsCollaboratorOnRepo(self):
        repo = mock.MagicMock()
        self.jb.addAsCollaboratorOnRepo(repo)
        repo.add_to_collaborators.assert_called_once_with('testJucyBot')
