from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from scipyshare.user.forms import LoginForm

def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        next = request.POST.get('next', '')
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not next:
                        next = login_page
                    return redirect(next)
                else:
                    form.errors['__all__'] = 'This account is disabled.'
            else:
                form.errors['__all__'] = 'Invalid login.'
    else:
        form = LoginForm()
        next = request.GET.get('next', '')

    return render_to_response('user/login.html',
                              dict(form=form, user=request.user, next=next),
                              context_instance=RequestContext(request)
                              )

def logout_page(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
    next = request.POST.get('next', login_page)
    return redirect(next)
