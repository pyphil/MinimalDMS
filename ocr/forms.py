from cgitb import strong
from django.forms import ModelForm
from .models import Document, Tag
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
            'tags',
            'file',
        )

        labels = {
            'name': mark_safe('<strong>Name/Bemerkung</strong>'),
            'status': mark_safe('<strong>Status</strong>'),
            'doctype': mark_safe('<strong>Dokumentenart</strong>'),
            'docdate': mark_safe('<strong>Datum</strong>'),
            'tags': mark_safe('<strong>Tags</strong>'),
            'file': mark_safe('<strong>Dateiupload</strong>'),
        }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.DateInput({'type': 'date', 'class': 'form-control', 'style': 'width: 150px; height: 38px;'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DocumentFormInput(ModelForm):
    class Meta:
        model = Document

        fields = (
            'name',
            'status',
            'doctype',
            'docdate',
            'tags',
        )

        labels = {
            'name': mark_safe('<strong>Name/Bemerkung</strong>'),
            'status': mark_safe('<strong>Status</strong>'),
            'doctype': mark_safe('<strong>Dokumentenart</strong>'),
            'docdate': mark_safe('<strong>Datum</strong>'),
            'tags': mark_safe('<strong>Tags</strong>'),
        }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.DateInput({'type': 'date', 'class': 'form-control', 'style': 'width: 150px; height: 38px;'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
        }


class DocumentFormEdit(ModelForm):
    class Meta:
        model = Document
        fields = (
            'name',
            'status',
            'doctype',
            'docdate',
            'tags',
            'file',
        )

        labels = {
            'name': mark_safe('<strong>Name/Bemerkung</strong>'),
            'status': mark_safe('<strong>Status</strong>'),
            'doctype': mark_safe('<strong>Dokumentenart</strong>'),
            'docdate': mark_safe('<strong>Datum</strong>'),
            'tags': mark_safe('<strong>Tags</strong>'),
            'file': mark_safe('<strong>Neue Version hochladen</strong>'),
        }

        widgets = {
            'name': forms.TextInput(attrs={'onfocus': 'hide_spinner()', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctype': forms.Select(attrs={'class': 'form-select'}),
            'docdate': forms.DateInput({'type': 'date', 'class': 'form-control', 'style': 'width: 150px; height: 38px;'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'mycol'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
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