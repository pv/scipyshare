from django import forms

from scipyshare.catalog.models import Entry, License

class EntryForm(forms.Form):
    title = forms.CharField(max_length=256)
    description = forms.CharField()

    license = forms.ModelChoiceField(License.objects.all(), empty_label=None)
    author = forms.CharField(max_length=256)
    entry_type = forms.ChoiceField(choices=Entry.ENTRY_TYPE_CHOICES)
    url = forms.CharField()
    pypi_name = forms.CharField(max_length=256)
