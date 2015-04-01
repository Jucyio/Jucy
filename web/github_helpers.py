import github

E_HOOK_ALREADY_EXISTS = u'Hook already exists on this repository'

def isGithubExceptionMessage(e, message):
    """Returns True if a GithubException was raised for a single error
    matching the provided message.
    """
    if e.status != 422:
        return False
    if not e.data:
        return False
    if not u'errors' in e.data or len(e.data[u'errors']) != 1:
        return False
    if not u'message' in e.data[u'errors'][0]:
        return False
    return e.data[u'errors'][0][u'message'] == message
