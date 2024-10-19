from django.contrib import admin

from .models import Enquiry, Enquirylogs,StudentEnquiryModel

admin.site.register(Enquiry)
admin.site.register(Enquirylogs)
admin.site.register(StudentEnquiryModel)
