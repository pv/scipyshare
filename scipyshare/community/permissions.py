from django.core.exceptions import PermissionDenied as _PermissionDenied

def _as_require(check_func):
    def wrapper(*a, **kw):
        if not check_func(*a, **kw):
            raise _PermissionDenied()
    wrapper.__name__ = check_func.__name__
    wrapper.__doc__ = check_func.__doc__
    return wrapper

def require(check_func, *a, **kw):
    if not check_func(*a, **kw):
        raise _PermissionDenied()

#--

def can_edit_entry(user, entry):
    return user == entry.owner or user.is_staff

require_can_edit_entry = _as_require(can_edit_entry)

def can_create_entry(user):
    return user.is_authenticated()

require_can_create_entry = _as_require(can_create_entry)

def can_tag_entry(user, entry):
    return user.is_authenticated()

require_can_tag_entry = _as_require(can_tag_entry)

def can_comment(user):
    return user.is_authenticated()

require_can_comment = _as_require(can_comment)
