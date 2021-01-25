from django import forms
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ClixoveLibrary.constant import bs5_input
from .models import Register


class LoginSheet(forms.Form):
    username = forms.CharField(max_length=64, required=True,
                               widget=forms.TextInput(bs5_input))
    password = forms.CharField(widget=forms.PasswordInput(bs5_input),
                               max_length=64, required=True)


def login_view(req):
    context = {
        "LoginSheet": LoginSheet(),
    }
    return render(req, "mylogin/home.html", context)


@require_POST
@csrf_exempt
def mylogin(req):
    sheet1 = LoginSheet(req.POST)
    if not sheet1.is_valid():
        return redirect('/traceback/login-form-not-valid/home')
    user = authenticate(req,
                        username=sheet1.cleaned_data['username'],
                        password=sheet1.cleaned_data['password'])
    if not user:
        return redirect('/traceback/password-error/home')
    login(req, user)
    return redirect('/library')


class RegisterSheet(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(bs5_input),
        label="Username", min_length=6, max_length=18,
        required=True,
        help_text="<small>English characters and digits (6-18) only.</small>",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(bs5_input),
        label="Password", required=True,
        min_length=4, max_length=16,
        help_text="<small>English characters and digits (4-16) only.</small>",
    )
    password_again = forms.CharField(
        widget=forms.PasswordInput(bs5_input),
        label="Password Again", required=False,
        min_length=4, max_length=16,
    )
    bio = forms.CharField(
        widget=forms.Textarea(bs5_input),
        label="Biography", required=False, max_length=500,
        help_text="<small>Information that is showed to admission staffs of the group. "
                  "Max lengthen 500 characters.</small>"
    )
    group = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(bs5_input),
        choices=[(x.id, x.name) for x in Group.objects.all()],
        required=True,
        help_text="<small>Press `Ctrl` to select multiple values.<br>Press `Shift` to select"
                  "continuous values.</small>"
    )


def register_view(req):
    context = {
        'RegisterSheet': RegisterSheet(),
    }
    return render(req, "mylogin/register.html", context)


@csrf_exempt
@require_POST
def register(req):
    register_sheet = RegisterSheet(req.POST)
    if not (
        register_sheet.is_valid() and
        register_sheet.cleaned_data['password'] == register_sheet.cleaned_data['password_again']
    ):
        return redirect('/traceback/register-form-not-valid/register')
    for g in register_sheet.cleaned_data['group']:
        new_register = Register(
            username=register_sheet.cleaned_data['username'],
            password=register_sheet.cleaned_data['password'],
            bio=register_sheet.cleaned_data['bio'],
            group_id=int(g)
        )
        new_register.save()
    return redirect('/mylogin/register')


@login_required(login_url='/home')
def mylogout(req):
    logout(req)
    return redirect('/home')


@permission_required('mylogin.view_register', login_url='/library')
def waitlist_view(req):
    context = {
        'NewUserTable': Register.objects.filter(group__in=req.user.groups.all()),
    }
    return render(req, "mylogin/waitlist.html", context)


@permission_required(('mylogin.add_register', 'mylogin.delete_register',
                      'mylogin.change_register'), login_url='/library')
@csrf_exempt
@require_POST
def admit(req):
    del_list = req.POST.getlist('tasks-index')
    if req.POST['action'] == 'Admit':
        for index in del_list:
            application = Register.objects.get(id=int(index))
            new_user = User(username=application.username)
            # check if username is unique
            unique_checks, date_checks = new_user._get_unique_checks()
            errors = new_user._perform_unique_checks(unique_checks)
            if errors:
                application.bio += "\nFAIL: the username is a duplicate of other users."
                application.save()
            else:
                new_user.set_password(application.password)
                new_user.save()
                application.group.user_set.add(new_user)
                application.delete()
    elif req.POST['action'] == 'Reject':
        for index in del_list:
            application = Register.objects.get(id=int(index))
            application.delete()
    elif req.POST['action'] == 'Upgrade':
        for index in del_list:
            application = Register.objects.get(id=int(index))
            user = authenticate(username=application.username, password=application.password)
            if user:
                application.group.user_set.add(user)
                application.delete()
            else:
                application.bio += "\nFAIL: the username and password do not match."
                application.save()
    return redirect('/library')
