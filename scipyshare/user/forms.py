from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=256)
    password = forms.CharField(max_length=256,
                               widget=forms.PasswordInput(render_value=False))
