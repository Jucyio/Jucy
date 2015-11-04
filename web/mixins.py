import labels
import github
import github_helpers

class GithubClientMixin():
    '''
    Mixin that encapsulate all the Github client functionalities.
    '''

    def is_collaborator_on_repo(self, repo):
        return repo.has_in_collaborators(self.login)

    def add_as_collaborator_on_repo(self, repo):
        repo.add_to_collaborators(self.login)

    def get_label_object(self, repo, label_name):
        key = (repo.full_name, label_name)
        if key in self.label_objects:
            return self.label_objects[key]
        label = repo.get_label(label_name)
        self.label_objects[key] = label
        return label

    def create_issue(self, repo_fullname, title, contents, label_name):
        body = self.format_issue(contents, label_name)
        repo = self.gh.get_repo(repo_fullname)
        return repo.create_issue(
            title,
            body=body,
            labels=[self.get_label_object(repo, label_name)])

    def change_issue_label(self, issue, repository, label_name):
        labels = repository.get_labels()
        issue_labels = issue.get_labels()
        label = next((label for label in labels if label.name == label_name), None)
        if not label:
            return
        for issue_label in issue_labels:
            if issue_label.name != label_name:
               issue.remove_from_labels(label)
        issue.set_labels(label)

    def user(self):
        return self.gh.get_user()

    def repo(self, repo):
        return self.gh.get_repo(repo)

    def format_issue(self, contents, label_name):
        # TODO(db0): Specify the boilerplate content for Jucy issues.
        boilerplate = """*This issue was filed by Jucy*
Category: %(label_name)s

%(contents_as_quote)s
"""
        contents_as_quote = textwrap.fill(contents,
                                          initial_indent='> ',
                                          subsequent_indent='> ')
        return boilerplate % {
            'label_name': label_name,
            'contents_as_quote': contents_as_quote,
        }
