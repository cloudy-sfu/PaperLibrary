from django.db import models
from django.contrib.auth.models import Group, User
from django.conf.global_settings import MEDIA_ROOT
from os.path import join


class GroupStorage(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    user_init_storage = models.IntegerField(verbose_name="Default User Storage (MB)", default=0)

    def __str__(self):
        return self.group.name


class UserStorage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specific_storage = models.IntegerField(verbose_name="Purchased Storage (MB)", default=0)

    def total_storage(self):
        groups = self.user.groups.all()
        storage_box = GroupStorage.objects.filter(group__in=groups)
        return sum([x.user_init_storage for x in storage_box]) + self.specific_storage

    def __str__(self):
        return self.user.username

    def upload_permission(self, new_file):
        return self.used_storage_bytes() + new_file.size <= self.total_storage() * 1024 ** 2

    def used_storage_bytes(self):
        users_projects = Project.objects.filter(user=self.user)
        users_papers = Paper.objects.filter(project__in=users_projects)
        return sum([x.file.size for x in users_papers])


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Paper(models.Model):
    project = models.ForeignKey(Project, models.CASCADE)
    file = models.FileField(upload_to=join(MEDIA_ROOT, 'papers/'))

    def __str__(self):
        return self.file.name
