import re

from django.db import models
from django.contrib.auth.models import User

from scipyshare.catalog.models import Entry

class Tag(models.Model):
    """
    Free-form tags and trove classifiers
    """

    name = models.SlugField(unique=True,
                            help_text="name *and* slug for the tag")
    description = models.TextField(help_text="description for the tag")

    entries = models.ManyToManyField(Entry, related_name="tags")

    # --

    def __str__(self):
        return self.name
