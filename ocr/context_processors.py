from .models import Document
from datetime import date


def get_resubmission_files(request):
    today = date.today()
    obj = Document.objects.filter(resubmission__lte=today).order_by('resubmission')
    files = []
    for file in obj:
        if file.status.id == 3:
            files.append({'name': file.name, 'id': file.id, 'resubmission_date': file.resubmission})
    return {
        'files': files
    }
