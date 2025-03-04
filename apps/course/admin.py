from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(CourseModel)
admin.site.register(CourseBookModel)
admin.site.register(CourseExamModel)
admin.site.register(CourseSubjectModel)