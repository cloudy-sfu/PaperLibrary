from random import randint

from django import forms
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ClixoveLibrary.constant import bs5_input
from .models import *


class AddPaperSheet(forms.Form):
    file = forms.FileField(widget=forms.FileInput(bs5_input))

    def load_project_menu(self, user):
        self.fields['project'] = forms.ModelChoiceField(
            widget=forms.Select(bs5_input),
            queryset=Project.objects.filter(user=user)
        )


class NewTaskSheet(forms.Form):
    name = forms.CharField(widget=forms.TextInput(bs5_input))


class MoveTo(forms.Form):
    def load_choices(self, user):
        self.fields['project'] = forms.ModelChoiceField(
            widget=forms.Select(bs5_input),
            label='Move To',
            queryset=Project.objects.filter(user=user),
            required=False
        )


@permission_required('papermanager.view_paper', login_url="/home")
def library_view(req):
    my_storage, created = UserStorage.objects.get_or_create(user=req.user)
    if created:
        my_storage.save()
    total_space = my_storage.total_storage()
    used_space = my_storage.used_storage_bytes()
    if used_space == 0:
        rate_space = 0
    else:
        rate_space = used_space / 10485.76 / total_space
    add_paper_sheet = AddPaperSheet()
    add_paper_sheet.load_project_menu(req.user)
    move_to = MoveTo()
    move_to.load_choices(req.user)
    context = {
        "Papers": Paper.objects.filter(project__user=req.user).order_by('project_id'),
        "Storage": total_space,
        "UsedStorage": used_space,
        "RateStorage": rate_space,
        "NewPaper": add_paper_sheet,
        # "NewProject": ,
        "MoveTo": move_to,
    }
    return render(req, "library/main.html", context)


@permission_required('papermanager.add_paper', login_url='/library')
@require_POST
@csrf_exempt
def add_paper(req):
    add_paper_sheet = AddPaperSheet(req.POST, req.FILES)
    add_paper_sheet.load_project_menu(req.user)
    if not add_paper_sheet.is_valid():
        return redirect('/traceback/sheet-not-valid/add-paper')
    project_id = add_paper_sheet.cleaned_data['project']
    new_paper = Paper(
        project=Project.objects.get(id=project_id),
        file=add_paper_sheet.cleaned_data['file']
    )
    my_storage = UserStorage.objects.get(user=req.user)
    if not my_storage.upload_permission(new_paper.file):
        return redirect('/traceback/file-exceed/add-paper')
    new_paper.save()
    return redirect('/library')


@permission_required('papermanager.add_project', login_url='/library')
@csrf_exempt
@require_POST
def add_project(req):
    new_project_raw = NewTaskSheet(req.POST)
    if not new_project_raw.is_valid():
        return redirect('/traceback/sheet-not-valid/library')
    new_project = Project(user=req.user, name=new_project_raw.cleaned_data['name'])
    new_project.save()
    return redirect('/library/projects')


class ChangePaperSheet(forms.Form):
    action = forms.CharField(widget=forms.Select(choices=['Delete', 'Move']))

    def load_choices(self, user):
        self.fields['paper'] = forms.ModelMultipleChoiceField(Paper.objects.filter(project__user=user))
        self.fields['project'] = forms.ModelChoiceField(Project.objects.filter(user=user), required=False)


@permission_required('papermanager.change_paper', login_url='/library')
@csrf_exempt
@require_POST
def change_papers(req):
    cps = ChangePaperSheet(req.POST)
    cps.load_choices(req.user)
    if not cps.is_valid():
        return redirect('/traceback/sheet-not-valid/library')
    if cps.cleaned_data['action'] == 'Delete':
        delete_project(cps.cleaned_data['paper'])
    elif cps.cleaned_data['action'] == 'Move':
        new_project = cps.cleaned_data['project']
        for paper in cps.cleaned_data['paper']:
            if paper.project == new_project:
                continue
            paper.project = new_project
            paper.save()
    return redirect('/library')


@permission_required('papermanager.delete_paper', login_url='/library')
def delete_project(paper_list):
    for paper in paper_list:
        paper.delete()


@permission_required('papermanager.view_project', login_url='/library')
def projects_view(req):
    context = {
        "ProjectsTable": Project.objects.filter(user=req.user),
        "NewProject": NewTaskSheet({'name': f'Project-{randint(10000, 99999)}'}),
    }
    return render(req, "library/projects.html", context)


class DeleteProjectSheet(forms.Form):
    def load_choices(self, user):
        self.fields['project'] = forms.ModelMultipleChoiceField(
            Project.objects.filter(user=user)
        )


@permission_required('papermanager.delete_project', login_url='/library')
@csrf_exempt
@require_POST
def delete_projects(req):
    dps = DeleteProjectSheet(req.POST)
    dps.load_choices(req.user)
    if not dps.is_valid():
        redirect('traceback/sheet-not-valid/projects')
    for project in dps.cleaned_data['project']:
        project.delete()
    return redirect('/library/projects')
