from django.shortcuts import redirect, render
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
import io
from .forms import DocumentForm, DocumentFormEdit, DocumentFormInput, TagForm
from .models import Document, Version, Tag, Status, Doctype
from django.http import FileResponse
from django.conf import settings
import os
import datetime
import shutil
from uuid import uuid4


def home(request):
    f = DocumentForm()

    inbox_files = get_inbox_files()  

    if request.method == 'POST':
        f = DocumentForm(request.POST, request.FILES)
        if f.is_valid():
            f.save()
            instance = f.save(commit=False)
            instance.filename = instance.file.name.split('/')[2]
            instance.filefolder = instance.file.name.split('/')[1]
            text = ocr_scan(instance.file.path)
            instance.text = text
            instance.save()
            return redirect('/archive/')

    return render(request, 'home.html', {'form': f, 'inbox_files': inbox_files})


def scaninput(request):
    inbox_files = get_inbox_files()  

    return render(request, 'scaninput.html', {'inbox_files': inbox_files})


def inbox(request):
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
            text = ocr_scan(input_path)
            instance.text = text
            os.mkdir(dest_path)
            shutil.move(input_path, dest_path)
            instance.file = 'data/' + request.POST.get('save')
            instance.filename = request.POST.get('save')
            instance.filefolder = uuid_dir
            instance.save()
            return redirect('/archive/')

    return render(request, 'inbox.html', {'form': f, 'file': file, })


def edit(request, id):
    obj = Document.objects.get(id=id)
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

    if request.method == 'GET':
        f = DocumentFormEdit(instance=obj)
        return render(request, 'edit.html', {
            'form': f,
            'date': obj.date,
            'filename': obj.filename,
            'versions': versions,
            }
        )
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
                text = ocr_scan(instance.file.path)
                instance.text = text
                instance.save()
        current_status = ""
        if request.GET.get('current_status') != "None":
            current_status = request.GET.get('current_status')
        return redirect(f"/archive/?status={current_status}&search=&submit=submit")


def ocr_scan(filepath):
    # get text from pdf
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # always add complete text from images to text variable as well
    # if no text in pdf: convert to image and then to searchable pdf
    images = convert_from_path(filepath, dpi=300, fmt='tiff')
    writer = PdfWriter()
    if text == "":
        for image in images:
            page = pytesseract.image_to_pdf_or_hocr(image, lang="deu", extension='pdf')
            pdf = PdfReader(io.BytesIO(page))
            text += pytesseract.image_to_string(image, lang="deu")
            writer.add_page(pdf.pages[0])
            # export pdf to same filename as searchable pdf if only image
            with open(filepath, 'wb') as f:
                writer.write(f)
    else:
        for image in images:
            text += pytesseract.image_to_string(image, lang="deu")

    return text


def archive(request):
    tags = Tag.objects.all()
    status_options = Status.objects.all()
    doctypes = Doctype.objects.all()
    if request.GET.get('submit'):
        search_strings = request.GET.get('search').split(" ")
        for search_string in search_strings:
            docs = (
                Document.objects.filter(text__icontains=search_string) | 
                Document.objects.filter(name__icontains=search_string) | 
                Document.objects.filter(filename__icontains=search_string)
            )
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
        return render(request, 'archive.html', {
            'docs': docs,
            'tags': tags,
            'status_options': status_options,
            'current_status': current_status,
            'current_doctype': current_doctype,
            'doctypes': doctypes,
            'search_text': request.GET.get('search'),
            'checked_tags': checked_tags,
            }
        )
    if request.GET.get('delete_search'):
        return redirect('archive')
    else:
        return render(request, 'archive.html', {'tags': tags, 'status_options': status_options, 'doctypes': doctypes})


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


def download(request, filefolder, filename):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/data/' + filefolder + '/' + filename, 'rb'),
        as_attachment=False,
        filename=filename
    )


def download_inbox(request, file):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/inbox/' + file, 'rb'),
        as_attachment=False,
        filename=file
    )
