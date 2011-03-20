import re

from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.comments.signals import comment_will_be_posted

from scipyshare.catalog.models import Entry
from scipyshare.community import permissions


#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

class TagCategory(models.Model):
    class Meta:
        ordering = ("name",)

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()

class Tag(models.Model):
    """
    Free-form tags and trove classifiers
    """

    class Meta:
        ordering = ("name",)

    name = models.SlugField(unique=True,
                            help_text="name *and* slug for the tag")
    description = models.TextField(help_text="description for the tag")
    category = models.ForeignKey(TagCategory, related_name="tags")

    # --

    def __str__(self):
        return self.name

class TagAssignment(models.Model):
    """
    Tag assignment
    """

    class Meta:
        unique_together = (("tag", "entry", "user"),)

    tag = models.ForeignKey(Tag, related_name="tag_assignments")
    entry = models.ForeignKey(Entry, related_name="tag_assignments")
    user = models.ForeignKey(User, related_name="tag_assignments")

    score = models.FloatField()

    #--

    @classmethod
    @transaction.commit_on_success
    def assign_tags(cls, user, entry, tags_to_score):
        TagAssignment.objects.filter(user=user, entry=entry).delete()
        for tag_name, score in tags_to_score.iteritems():
            tag = Tag.objects.get(name=tag_name)
            x = TagAssignment(tag=tag, entry=entry, user=user, score=score)
            x.save()

        TagCache.recompute(entry)

class TagCache(models.Model):
    class Meta:
        unique_together = (("tag", "entry"),)
        ordering = ('-score',)

    tag = models.ForeignKey(Tag, related_name="+")
    entry = models.ForeignKey(Entry, related_name="tags")
    score = models.FloatField()

    def __str__(self):
        return "%s:%s (%g)" % (self.entry, self.tag, self.score)


    @classmethod
    def _recompute_one(cls, entry):
        assignments = TagAssignment.objects.filter(entry=entry).values('tag', 'entry').annotate(models.Sum('score'))
        for x in assignments:
            if x['score__sum'] > 0:
                cache = TagCache(tag=Tag.objects.get(id=x['tag']),
                                 entry=entry,
                                 score=x['score__sum'])
                cache.save()

    @classmethod
    @transaction.commit_on_success
    def recompute(cls, entry):
        TagCache.objects.filter(entry=entry).delete()
        cls._recompute_one(entry)

    @classmethod
    @transaction.commit_on_success
    def recompute_all(cls):
        TagCache.objects.all().delete()
        for entry in Entry.objects.all():
            cls._recompute_one(entry)


#------------------------------------------------------------------------------
# Comments
#------------------------------------------------------------------------------

def _comment_pre_save(sender, comment, request, **kw):
    if not permissions.can_comment(request.user):
        return False
    comment.user = request.user
    return True

comment_will_be_posted.connect(_comment_pre_save)
