import json
import magic

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.views.generic import View

from cms.apps.media.models import File


class ImageUploadView(View, LoginRequiredMixin):
    def get(self, request):
        file_list = [{
            'id': file.pk,
            'image': file.file.url,
            'title': file.title,
            'alt_text': file.alt_text,
            'size': filesizeformat(file.file.size),
        } for file in File.objects.all()]

        return JsonResponse(mark_safe(json.dumps(file_list)), safe=False)

    def post(self, request):
        if request.POST.get('title', False) and request.FILES['file']:
            ALLOWED_FILETYPES = {
                'image/jpeg',
                'image/gif',
                'image/png',
                'image/tiff',
            }

            image = request.FILES['file']
            guessed_filetype = magic.from_buffer(image.read(1024), mime=True)
            image.seek(0)
            claimed_filetype = image.content_type
            if (claimed_filetype == guessed_filetype) and (guessed_filetype in ALLOWED_FILETYPES):
                uploaded_file = File(
                    title=request.POST.get('title', ''),
                    attribution=request.POST.get('attribution', ''),
                    copyright=request.POST.get('copyright', ''),
                    alt_text=request.POST.get('alt_text', ''),
                )
                uploaded_file.file.save(
                    image.name,
                    image
                )
                uploaded_file.save()
                return JsonResponse({
                    'file_url': uploaded_file.file.url,
                    'file_title': uploaded_file.title,
                    'file_alt': uploaded_file.alt_text,
                })
            return JsonResponse({'fail_message': 'File type not allowed'}, status=400)
        return JsonResponse({'fail_message': 'Please provide both a file and title.'}, status=400)
