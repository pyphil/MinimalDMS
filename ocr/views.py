from django.shortcuts import redirect, render
import pytesseract
# from PIL import Image
from pdf2image import convert_from_path
import PyPDF2
import io
from .forms import DocumentForm, DocumentFormEdit
from .models import Document, Version, Tag, Status, Doctype
from django.http import FileResponse
from django.conf import settings
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def home(request):
    if request.method == 'GET':
        f = DocumentForm()

        """ Add text to PDF using PyPDF2 and reportlab
        packet = io.BytesIO()
        # create a new PDF with Reportlab
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(0, 0, "Hello world")
        can.save()

        # move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open("searchable.pdf", "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        # finally, write "output" to a real file
        outputStream = open("destination.pdf", "wb")
        output.write(outputStream)
        outputStream.close()
        END """

        return render(request, 'home.html', {'form': f})
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
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Users\phil\AppData\Local\Tesseract-OCR\tesseract.exe'
    # text = pytesseract.image_to_string('ocr/Datenschutz.jpg', lang='deu')

    # get text from pdf
    reader = PyPDF2.PdfFileReader(filepath)
    pageObj = reader.getNumPages()
    for page_count in range(pageObj):
        page = reader.getPage(page_count)
        text = page.extractText()

    # if only image in pdf, convert to searchable pdf
    if text == "":
        images = convert_from_path(filepath, dpi=300)
        pdf_writer = PyPDF2.PdfFileWriter()

        for image in images:
            text += pytesseract.image_to_string(image, lang='deu')
            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
            pdf_writer.addPage(pdf.getPage(0))
            # export the searchable PDF to searchable.pdf
            with open(filepath, "wb") as f:
                pdf_writer.write(f)
    return text


def archive(request):
    tags = Tag.objects.all()
    status = Status.objects.all()
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
        return render(request, 'archive.html', {
            'docs': docs,
            'tags': tags,
            'status': status, 
            'doctypes': doctypes,
            'search_text': request.GET.get('search'),
            'checked_tags': checked_tags
            }
        )
    else:
        return render(request, 'archive.html', {'tags': tags, 'status': status, 'doctypes': doctypes})


def download(request, filefolder, filename):
    return FileResponse(
        open(settings.MEDIA_ROOT + '/data/' + filefolder + '/' + filename, 'rb'),
        as_attachment=False,
        filename=filename
    )
