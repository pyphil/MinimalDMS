from django.shortcuts import redirect, render
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from .forms import DocumentForm, DocumentFormEdit, DocumentFormInput, TagForm, DoctypeForm, PersonForm
from .models import Document, Version, Tag, Status, Doctype, Person
from django.http import FileResponse
from django.conf import settings
import os
from io import BytesIO
import datetime
import shutil
from uuid import uuid4
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from threading import Thread


class OCRThread(Thread):
    def __init__(self, instance, request):
        super(OCRThread, self).__init__()
        self.instance = instance
        self.request = request

    def run(self):
        messages.error(self.request, f'<i class="bi bi-exclamation-triangle-fill"></i> <b>{self.instance.name}</b> wird im Hintergrund verarbeitet.')
        self.instance.filename = self.instance.file.name.split('/')[2]
        self.instance.filefolder = self.instance.file.name.split('/')[1]
        text, error = ocr_scan(self.instance.file.path)
        self.instance.text = text
        if not error:
            self.instance.save()
        else:
            self.instance.delete()
            # fail silently at the moment
            # messages.error(self.request, f'<i class="bi bi-exclamation-triangle-fill"></i> Beim Speichern von <b>{self.instance.name}</b> ist ein Fehler aufgetreten. Es handelt sich nicht um eine lesbare PDF-Datei.')


def inbox(request):
    f = DocumentForm()

    inbox_files = get_inbox_files()  

    if request.method == 'POST':
        f = DocumentForm(request.POST, request.FILES)
        if f.is_valid():
            f.save()
            instance = f.save(commit=False)
            thread = OCRThread(instance, request)
            thread.start()
            return redirect('archive')

    return render(request, 'inbox.html', {'form': f, 'inbox_files': inbox_files})


def scaninput(request):
    inbox_files = get_inbox_files()

    return render(request, 'scaninput.html', {'inbox_files': inbox_files})


def inbox_scaninput(request):
    f = DocumentFormInput()

    if request.POST.get('inbox_file'):
        file = request.POST.get('inbox_file')

    if request.POST.get('save'):
        f = DocumentFormInput(request.POST)
        if f.is_valid():
            f.save()
            instance = f.save(commit=False)
            uuid_dir = str(uuid4())
            input_path = os.path.join(settings.MEDIA_ROOT, 'inbox', request.POST.get('save'))
            dest_path = os.path.join(settings.MEDIA_ROOT, 'data', uuid_dir)
            text, error = ocr_scan(input_path)
            instance.text = text
            os.mkdir(dest_path)
            shutil.move(input_path, dest_path)
            instance.file = 'data/' + request.POST.get('save')
            instance.filename = request.POST.get('save')
            instance.filefolder = uuid_dir
            if not error:
                instance.save()
                return redirect('archive')
            else:
                instance.delete()
                messages.error(request, f'<i class="bi bi-exclamation-triangle-fill"></i> Beim Speichern von <b>{instance.name}</b> ist ein Fehler aufgetreten. Es handelt sich nicht um eine lesbare PDF-Datei.')

    return render(request, 'inbox_scaninput.html', {'form': f, 'file': file, })


def edit(request, id):
    obj = Document.objects.get(id=id)
    tags = Tag.objects.all()
    oldfile = obj.file
    try:
        versions = Version.objects.filter(docid=id)
        v = Version.objects.filter(docid=id).last()
    except Exception:
        v = 0
    else:
        if v is not None:
            v = v.version
        else:
            v = 0

    if request.method == 'POST':
        f = DocumentFormEdit(request.POST, request.FILES, instance=obj)
        if f.is_valid():
            # check if new version and save old file in Version model
            if 'file' in f.changed_data:
                Version.objects.create(
                    docid=id,
                    version=v + 1,
                    date=obj.date,
                    file=oldfile,
                    filefolder=obj.filefolder,
                    filename=obj.filename,
                )
            f.save()
            if 'file' in f.changed_data:
                instance = f.save(commit=False)
                instance.filename = instance.file.name.split('/')[2]
                instance.filefolder = instance.file.name.split('/')[1]
                text, error = ocr_scan(instance.file.path)
                instance.text = text
                if not error:
                    instance.save()
                else:
                    messages.error(request, f'<i class="bi bi-exclamation-triangle-fill"></i> <small>Beim Speichern von einer neuen Dateiversion von <b>{instance.name}</b> ist ein Fehler aufgetreten. Es handelt sich nicht um eine lesbare PDF-Datei.</small>')
        current_status = ""
        if request.GET.get('current_status') != "None":
            current_status = request.GET.get('current_status')
        if request.GET.get('current_doctype') != "None":
            current_doctype = request.GET.get('current_doctype')
        if request.GET.get('search_text') != "None":
            search_text = request.GET.get('search_text')
        if request.GET.get('person') != "None":
            person = request.GET.get('person')
        checked_tags = ""
        for i in tags:
            if request.GET.get(i.tag) == "1":
                checked_tags += f"&{i.tag}=1"
        return redirect(f"/?status={current_status}&search={search_text}&doctype={current_doctype}&person={person}&submit=submit{checked_tags}")

    f = DocumentFormEdit(instance=obj)
    return render(request, 'edit.html', {
        'form': f,
        'date': obj.date,
        'filename': obj.filename,
        'versions': versions,
        }
    )


def ocr_scan(filepath):
    error = None
    text = ""
    try:
        # get text from pdf
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text()

        # always add complete text from images to text variable as well
        # if no text in pdf: convert to image and then to searchable pdf
        images = convert_from_path(filepath, dpi=300, fmt='tiff')
        writer = PdfWriter()
        if text == "":
            for image in images:
                page = pytesseract.image_to_pdf_or_hocr(image, lang="deu", extension='pdf')
                pdf = PdfReader(BytesIO(page))
                text += pytesseract.image_to_string(image, lang="deu")
                writer.add_page(pdf.pages[0])
            # export pdf to same filename as searchable pdf if only image
            with open(filepath, 'wb') as f:
                writer.write(f)
        else:
            for image in images:
                text += pytesseract.image_to_string(image, lang="deu")
    except Exception:
        error = True

    return text, error


def archive(request):
    tags = Tag.objects.all()
    status_options = Status.objects.all()
    doctypes = Doctype.objects.all()
    persons = Person.objects.all()
    if request.GET.get('delete_search'):
        return redirect('archive')
    if request.GET.get('form_submitted'):
        search_strings = request.GET.get('search').split(" ")
        for search_string in search_strings:
            docs = (
                Document.objects.filter(text__icontains=search_string) | 
                Document.objects.filter(name__icontains=search_string) | 
                Document.objects.filter(filename__icontains=search_string) | 
                Document.objects.filter(notes__icontains=search_string)
            ).order_by('-docdate')
        checked_tags = []
        for i in tags:
            if request.GET.get(i.tag) == "1":
                docs = docs.filter(tags__tag__icontains=i.tag)
                checked_tags.append(i)
        current_status = ""
        if request.GET.get('status'):
            current_status = request.GET.get('status')
            docs = docs.filter(status__status=current_status)
        current_doctype = ""
        if request.GET.get('doctype'):
            current_doctype = request.GET.get('doctype')
            docs = docs.filter(doctype__doctype=current_doctype)
        current_person = ""
        if request.GET.get('person'):
            current_person = request.GET.get('person')
            docs = docs.filter(person__person=current_person)
        docs = docs[:100]
        hundred_or_more = None
        if len(docs) == 100:
            hundred_or_more = True
        return render(request, 'archive.html', {
            'docs': docs,
            'tags': tags,
            'status_options': status_options,
            'current_status': current_status,
            'current_doctype': current_doctype,
            'current_person': current_person,
            'doctypes': doctypes,
            'persons': persons,
            'search_text': request.GET.get('search'),
            'checked_tags': checked_tags,
            'hundred_or_more': hundred_or_more,
            }
        )
    else:
        docs = Document.objects.all().order_by('-docdate')[:100]
        hundred_or_more = None
        if len(docs) == 100:
            hundred_or_more = True
        return render(request, 'archive.html', {
            'docs': docs,
            'tags': tags,
            'status_options': status_options,
            'doctypes': doctypes,
            'persons': persons,
            'hundred_or_more': hundred_or_more,
            }
        )


def get_inbox_files():
    # Define the directory path
    directory_path = settings.MEDIA_ROOT + '/inbox'

    # Initialize a list to store file information
    file_list = []

    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # List all files in the directory
        files = os.listdir(directory_path)

        # Loop through the files and gather information
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)

            # Check if the path is a file (not a directory)
            if os.path.isfile(file_path):
                # Get file creation time (you can also use other attributes like modification time)
                creation_time = os.path.getctime(file_path)

                # Append file information to the list
                file_list.append({
                    'filename': file_name,
                    'creation_time': datetime.datetime.fromtimestamp(creation_time),
                })

    # Render the template and pass the file_list data to it
    return file_list


def tags(request):
    tags = Tag.objects.all()
    new_form = TagForm()
    forms = []
    for tag in tags:
        forms.append(TagForm(instance=tag))

    if request.method == 'POST':
        if request.POST.get('save_new'):
            new_form = TagForm(request.POST)
            if new_form.is_valid():
                new_form.save()
                return redirect('tags')
        if request.POST.get('save_edited'):
            obj = Tag.objects.get(id=request.POST.get('save_edited'))
            edited_form = TagForm(request.POST, instance=obj)
            if edited_form.is_valid():
                edited_form.save()
                return redirect('tags')
        if request.POST.get('delete'):
            obj = Tag.objects.get(id=request.POST.get('delete'))
            if obj.get_number_of_items == 0:
                obj.delete()
                return redirect('tags')

    return render(request, "tags.html", {
        'tags': tags,
        'forms': forms,
        'new_form': new_form,
        }
    )


def doctypes(request):
    doctypes = Doctype.objects.all()
    new_form = DoctypeForm()
    forms = []
    for doctype in doctypes:
        forms.append(DoctypeForm(instance=doctype))

    if request.method == 'POST':
        if request.POST.get('save_new'):
            new_form = DoctypeForm(request.POST)
            if new_form.is_valid():
                new_form.save()
                return redirect('doctypes')
        if request.POST.get('save_edited'):
            obj = Doctype.objects.get(id=request.POST.get('save_edited'))
            edited_form = DoctypeForm(request.POST, instance=obj)
            if edited_form.is_valid():
                edited_form.save()
                return redirect('doctypes')
        if request.POST.get('delete'):
            obj = Doctype.objects.get(id=request.POST.get('delete'))
            if obj.get_number_of_items == 0:
                obj.delete()
                return redirect('doctypes')

    return render(request, "doctypes.html", {
        'doctypes': doctypes,
        'forms': forms,
        'new_form': new_form,
        }
    )


def persons(request):
    persons = Person.objects.all()
    new_form = PersonForm()
    forms = []
    for person in persons:
        forms.append(PersonForm(instance=person))

    if request.method == 'POST':
        if request.POST.get('save_new'):
            new_form = PersonForm(request.POST)
            if new_form.is_valid():
                new_form.save()
                return redirect('persons')
        if request.POST.get('save_edited'):
            obj = Person.objects.get(id=request.POST.get('save_edited'))
            edited_form = PersonForm(request.POST, instance=obj)
            if edited_form.is_valid():
                edited_form.save()
                return redirect('persons')
        if request.POST.get('delete'):
            obj = Person.objects.get(id=request.POST.get('delete'))
            if obj.get_number_of_items == 0:
                obj.delete()
                return redirect('persons')

    return render(request, "persons.html", {
        'persons': persons,
        'forms': forms,
        'new_form': new_form,
        }
    )


@login_required
def download(request, filefolder, filename):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/data/' + filefolder + '/' + filename, 'rb'),
        as_attachment=False,
        filename=filename
    )


@login_required
def download_inbox(request, file):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/inbox/' + file, 'rb'),
        as_attachment=False,
        filename=file
    )
