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
