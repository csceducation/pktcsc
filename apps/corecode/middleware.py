from django.shortcuts import redirect
from django.urls import reverse

from .models import AcademicSession, AcademicTerm



class LoginRequiredMiddleware:
    """
    Middleware to redirect unauthenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude redirection for the public view URL pattern
        excluded_url_pattern = '/enquiryform'

        # Check if the user is not authenticated and the requested URL does not match the excluded pattern
        if not request.user.is_authenticated and not request.path.startswith(excluded_url_pattern):
            # Exclude URLs with IDs after /public/student/
            if len(request.path.split('/')) < 4:
                return redirect('login')
        
        return self.get_response(request)
    
class SiteWideConfigs:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)

        request.current_session = current_session
        request.current_term = current_term

        response = self.get_response(request)

        return response
