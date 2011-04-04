Design
======

Below, some random musings on aims and how to get there.


Mission statement
-----------------

We want to share scientific know-how; the subset that can be written
down in Python.

We want an authoritative, permanent, and complete listing of what is
out there.

We want to be serious. The stuff here must be useful for scientific
research.

We want to be social. We want to provide feedback on what others do,
and suggest helpful pieces of know-how to them.

And we want to be lazy. Nothing should take too much effort or
resources. Running the site is no exception to this.


Sources of inspiration
----------------------

Where do scientists usually share their findings? Why, on the pages of
scientific journals of course.

This then collides with the social Web: we know wikis can work, blogs
show comments are an useful form of feedback, Stackoverflow shows how
users act as editors.

Thinking of a code sharing site as a "journal" at first sight seems a
bit strange, but thinking about the site as it publishing "articles"
can be conceptually helpful: Each article has a permanent location.
Several types of articles can be published (full packages, reference
cards to packages available elsewhere, wiki-like cookbook entries,
reviews, etc.).

Of course, many aspects of real journals are not practical: We
obviously don't have resources or the need for peer review, and so
there's no reason to not immediately publish anything submitted (any
review is done post-publication via comments etc.).  All of the
content should also be possible to revise easily, and some of it is
reasonable to have in a wiki-like form. The date of publication is
also not very important here.


Content to share
----------------

We want to run several types of articles:

(a) Hosted software.

    Code submitted by people directly to this site.

(b) Reference cards to software available elsewhere.

    For example, linking to PyPi or a home page elsewhere.

(c) Cookbook snippets.

    Code examples and snippets showing how to do something.

The three have different senses of ownership.

Those in category (a) should be editable only by the original
submitter: the code package and its documentation is a serious piece
of work, and this site provides the authoritative place for it.

Those in categories (b) and (c) are then more wiki-like entries. The
pieces can be improved and kept up to date by anyone with extra time
on his/her hands. These submissions are also always public domain.


Community features
------------------

The task of classification etc. is handed to the community.  We
provide support for:

- Tags.

  Tags are classified to different categories: topic, code maturity,
  usefulness, etc.

- Comments.

  Each entry gets a comments section. The comments should 'remember'
  which revision of the entry they refer to (if not current).

Tagging
-------

Tags are classified in tag categories.

Tag categories are managed by Editors only.

New tags can be created by all users, and edited by Editors.

Tag assignments can be made by all users. They are per-user, so each
user can have a different tag assignment for an entry.




Code Layout
===========

We'll try to roughly follow
`these instructions <http://ericholscher.com/projects/django-conventions/>`__.

The code is laid out as follows. The problem is split into as small
parts as possible.


Custom Django applications are put in
the ``scipyshare`` package::

    scipyshare/APPNAME/__init__.py
    scipyshare/APPNAME/*.py
    scipyshare/APPNAME/static/APPNAME/**
    scipyshare/APPNAME/templates/APPNAME/*.html
    scipyshare/APPNAME/templates/admin/APPNAME/*.html
    scipyshare/APPNAME/templatetags/*.py
    scipyshare/docs/*

and the main project resides in::

    deploy/
