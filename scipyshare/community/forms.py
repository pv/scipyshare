import time
import datetime

from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType

from django.contrib.comments.forms import CommentForm as _CommentForm, \
     COMMENT_MAX_LENGTH
from django.contrib.comments.models import Comment

class CommentForm(_CommentForm):
    def __init__(self, *a, **kw):
        _CommentForm.__init__(self, *a, **kw)
        del self.fields['name']
        del self.fields['email']
        del self.fields['url']

    def get_comment_create_data(self):
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
        )
