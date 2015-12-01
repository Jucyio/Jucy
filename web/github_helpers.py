E_HOOK_ALREADY_EXISTS = u'Hook already exists on this repository'


def matches_github_exception(e, description, code=422):
    """Returns True if a GithubException was raised for a single error
    matching the provided dict.

    The error code needs to be equal to `code`, unless code is
    None. For each field in `description`, the error must have an
    identical field. The error can have extraneous fields too. If
    multiple errors are present, this function returns False.
    """
    if e.status != code:
        return False
    if not e.data or u'errors' not in e.data or len(e.data[u'errors']) != 1:
        return False
    error = e.data['errors'][0]
    for k, v in description.iteritems():
        if k not in error or error[k] != v:
            return False
    return True


def is_github_exception_message(e, message):
    """Returns True if a GithubException was raised for a single error
    matching the provided message.
    """
    return matches_github_exception(e, {u'message': message})
