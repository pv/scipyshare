from django import forms

from scipyshare.catalog.models import Entry, License

#
# Entries
#

class EntryForm(forms.Form):
    title = forms.CharField(max_length=256)
    entry_type = forms.ChoiceField(choices=Entry.ENTRY_TYPE_CHOICES)

#
# Packages
#

class EditForm(forms.Form):
    def __init__(self, *a, **kw):
        files = kw.pop('files', [])
        forms.Form.__init__(self, *a, **kw)
        self.set_files(files)

    def set_files(self, files):
        if 'files' in self.fields:
            self.fields['files'].choices = [(x, x) for x in files]

class PackageForm(EditForm):
    description = forms.CharField(widget=forms.Textarea())

    license = forms.ModelChoiceField(License.objects.all(), empty_label=None)
    author = forms.CharField(max_length=256)
    url = forms.CharField(required=False)

    files = forms.MultipleChoiceField(choices=(), required=False)
    upload_file = forms.FileField(required=False)

    change_comment = forms.CharField(required=True, widget=forms.Textarea())

#
# Infos
#

class InfoForm(EditForm):
    description = forms.CharField(widget=forms.Textarea())

    license = forms.ModelChoiceField(License.objects.all(), empty_label=None)
    author = forms.CharField(max_length=256)

    url = forms.CharField()
    pypi_name = forms.CharField(max_length=256)

    change_comment = forms.CharField(required=True, widget=forms.Textarea())

#
# Snippets
#

class SnippetForm(EditForm):
    description = forms.CharField(widget=forms.Textarea())
    snippet = forms.CharField(required=False, widget=forms.Textarea())

    upload_file = forms.FileField(required=False)
    change_comment = forms.CharField(required=True, widget=forms.Textarea())
