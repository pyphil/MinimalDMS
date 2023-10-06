from cgitb import strong
from django.forms import ModelForm
from .models import Document, Tag, Doctype, Person
from django import forms
from django.utils.safestring import mark_safe


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = (
            'name',
            'status',
            'doctype',
            'docdate',
            'person',
            'tags',
            'file',
            'notes',
        )

        # labels = {
        #     'name': mark_safe('<strong>Name/Bemerkung</strong>'),
        #     'status': mark_safe('<strong>Status</strong>'),
        #     'doctype': mark_safe('<strong>Dokumentenart</strong>'),
        #     'docdate': mark_safe('<strong>Datum</strong>'),
        #     'tags': mark_safe('<strong>Tags</strong>'),
        #     'file': mark_safe('<strong>Dateiupload</strong>'),
        #     'notes': mark_safe('<strong>Notizen</strong>'),
        # }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.TextInput({'type': 'date', 'class': 'form-control'}),
            'person': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 120px'}),
        }


class DocumentFormInput(ModelForm):
    class Meta:
        model = Document

        fields = (
            'name',
            'status',
            'doctype',
            'docdate',
            'person',
            'tags',
            'notes',
        )

        # labels = {
        #     'name': mark_safe('<strong>Name/Bemerkung</strong>'),
        #     'status': mark_safe('<strong>Status</strong>'),
        #     'doctype': mark_safe('<strong>Dokumentenart</strong>'),
        #     'docdate': mark_safe('<strong>Datum</strong>'),
        #     'tags': mark_safe('<strong>Tags</strong>'),
        #     'notes': mark_safe('<strong>Notizen</strong>'),
        # }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.TextInput({'type': 'date', 'class': 'form-control'}),
            'person': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 120px'}),
        }


class DocumentFormEdit(ModelForm):
    class Meta:
        model = Document
        fields = (
            'name',
            'status',
            'doctype',
            'docdate',
            'resubmission',
            'person',
            'tags',
            'file',
            'notes',
        )

        # labels = {
        #     'name': mark_safe('<strong>Name/Bemerkung</strong>'),
        #     'status': mark_safe('<strong>Status</strong>'),
        #     'doctype': mark_safe('<strong>Dokumentenart</strong>'),
        #     'docdate': mark_safe('<strong>Datum</strong>'),
        #     'tags': mark_safe('<strong>Tags</strong>'),
        #     'file': mark_safe('<strong>Neue Version hochladen</strong>'),
        #     'notes': mark_safe('<strong>Notizen</strong>'),
        # }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.TextInput({'type': 'date', 'class': 'form-control'}),
            'resubmission': forms.TextInput({'type': 'date', 'class': 'form-control'}),
            'person': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 120px'}),
        }


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = [
            'tag'
        ]

        widgets = {
            'tag': forms.TextInput(attrs={'class': 'form-control'})
        }


class DoctypeForm(ModelForm):
    class Meta:
        model = Doctype
        fields = [
            'doctype'
        ]

        widgets = {
            'doctype': forms.TextInput(attrs={'class': 'form-control'})
        }


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = [
            'person'
        ]

        widgets = {
            'person': forms.TextInput(attrs={'class': 'form-control'})
        }
