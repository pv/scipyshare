from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from scipyshare.user.forms import LoginForm

def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    next = request.GET.get(login_page, 'next')
                    return redirect(next)
                else:
                    form.errors['__all__'] = 'This account is disabled.'
            else:
                form.errors['__all__'] = 'Invalid login.'
    else:
        form = LoginForm()

    return render_to_response('user/login.html',
                              dict(form=form, user=request.user),
                              context_instance=RequestContext(request)
                              )
