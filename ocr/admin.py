from django.contrib import admin
from .models import Document, Tag, Status, Doctype, Version


class DocumentCustomAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'doctype', 'date', 'filename')
    list_filter = ('name', 'status', 'doctype', 'date', 'filename')


# Register your models here.
admin.site.register(Document, DocumentCustomAdmin)
admin.site.register(Status)
admin.site.register(Doctype)
admin.site.register(Tag)
admin.site.register(Version)
