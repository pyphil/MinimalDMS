from django.db import models
from uuid import uuid4


class Status(models.Model):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.status


class Doctype(models.Model):
    doctype = models.CharField(max_length=30)

    def __str__(self):
        return self.doctype

    @property
    def get_number_of_items(self):
        number_of_items = len(Document.objects.filter(doctype=self.id))

        return number_of_items


class Person(models.Model):
    person = models.CharField(max_length=50)

    def __str__(self):
        return self.person


class Tag(models.Model):
    tag = models.CharField(max_length=30)

    def __str__(self):
        return self.tag

    @property
    def get_number_of_items(self):
        number_of_items = len(Document.objects.filter(tags=self.id))

        return number_of_items


class Document(models.Model):
    name = models.CharField(max_length=260)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING)
    doctype = models.ForeignKey(Doctype, on_delete=models.DO_NOTHING)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    date = models.DateTimeField(auto_now=True, null=True, blank=True)
    docdate = models.DateField()
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="data/" + str(uuid4()))
    filename = models.CharField(max_length=260, null=True, blank=True)
    filefolder = models.CharField(max_length=36, null=True, blank=True)
    notes = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Version(models.Model):
    docid = models.IntegerField()
    version = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    file = models.FileField()
    filename = models.CharField(max_length=260, null=True, blank=True)
    filefolder = models.CharField(max_length=36, null=True, blank=True)
