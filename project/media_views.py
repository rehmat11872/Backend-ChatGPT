from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import os
import mimetypes

@method_decorator(csrf_exempt, name='dispatch')
class MediaView(View):
    def get(self, request, path):
        # Add CORS headers
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        
        # Serve the file
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # Get content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Read and return file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = '*'
            return response
    
    def options(self, request, path):
        # Handle preflight requests
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        return response