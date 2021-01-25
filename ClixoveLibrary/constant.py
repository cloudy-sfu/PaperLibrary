from django.shortcuts import render


def traceback(request, guidance, retrieve):
    context = {"hint_info": content[guidance], "retrieve": short_link[retrieve]}
    return render(request, "traceback.html", context)


content = {
    'login-form-not-valid': 'Login form is not valid.',
    'password-error': 'Username or password is not correct.',
    'register-form-not-valid': 'Two fields of password are not the same, or the form is not valid.',
    'sheet-not-valid': 'The submission is not valid.',
    'file-exceed': 'You storage has used up, and there isn\'t enough space for this file.',
}
short_link = {
    'register': 'mylogin/register',
    'home': 'home',
    'library': 'library',
    'projects': 'library/projects',
}
bs5_input = {"class": "form-control form-group"}
