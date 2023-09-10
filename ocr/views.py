from django.shortcuts import redirect, render
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
import io
from .forms import DocumentForm, DocumentFormEdit
from .models import Document, Version, Tag, Status, Doctype
from django.http import FileResponse
from django.conf import settings


def home(request):
    f = DocumentForm()

    if request.method == 'POST':
        f = DocumentForm(request.POST, request.FILES)
        if f.is_valid():
            print("save")
            f.save()
            print("saved")
            instance = f.save(commit=False)
            instance.filename = instance.file.name.split('/')[2]
            instance.filefolder = instance.file.name.split('/')[1]
            text = ocr_scan(instance.file.path)
            instance.text = text
            instance.save()
            return redirect('/archive/')

    return render(request, 'home.html', {'form': f})


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
        return redirect('/archive/')


def ocr_scan(filepath):
    # get text from pdf
    reader = PdfReader(filepath)
    text = ""
    contains_images = False
    for page in reader.pages:
        text += page.extract_text()
        if page.images:
            contains_images = True
        for image_file_object in page.images:
            text += pytesseract.image_to_string(image_file_object.image, lang='deu')

    # if images in pdf, convert to searchable pdf
    if contains_images:
        images = convert_from_path(filepath, dpi=300, fmt='tiff')
        writer = PdfWriter()
        for image in images:
            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            pdf = PdfReader(io.BytesIO(page))
            writer.add_page(pdf.pages[0])
        # export pdf to same filename as searchable pdf
        with open(filepath, 'wb') as f:
            writer.write(f)

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
        current_status = None
        if request.GET.get('status'):
            current_status = request.GET.get('status')
            docs = docs.filter(status__status=current_status)
        return render(request, 'archive.html', {
            'docs': docs,
            'tags': tags,
            'status_options': status_options,
            'current_status': current_status,
            'doctypes': doctypes,
            'search_text': request.GET.get('search'),
            'checked_tags': checked_tags,
            }
        )
    else:
        return render(request, 'archive.html', {'tags': tags, 'status_options': status_options, 'doctypes': doctypes})


def download(request, filefolder, filename):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/data/' + filefolder + '/' + filename, 'rb'),
        as_attachment=False,
        filename=filename
    )
