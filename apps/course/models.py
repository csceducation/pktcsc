from django.db import models 
from django.urls import reverse
from apps.corecode.models import Subject , Book , Exam
class CourseModel(models.Model):
    status = models.CharField("Course Status",max_length=255,choices = [("Active","Active"),("Inactive","Inactive")] , default="Active")
    course_name  = models.CharField("Course Full Name",max_length=1024,default="",null=False)
    course_s_name  = models.CharField("Course Short Name",max_length=1024,default="",null=False)
    course_duration = models.CharField("Course Duration (* In Hours)",max_length=255,default= None)
    course_fee = models.IntegerField("Course Fee")
    def get_absolute_url(self):
        return reverse("details_course", kwargs={"pk": self.pk})
    def __str__(self) -> str:
        return f"{self.course_s_name}"
    
class CourseSubjectModel(models.Model):
    course = models.ForeignKey(CourseModel,on_delete=models.PROTECT)
    sub_name = models.ManyToManyField(Subject)
    def get_absolute_url(self):
        return reverse("details_course", kwargs={"pk": self.course.pk})

class CourseBookModel(models.Model):
    course = models.ForeignKey(CourseModel,on_delete=models.PROTECT)
    book_name = models.ManyToManyField(Book)
    def get_absolute_url(self):
        return reverse("details_course", kwargs={"pk": self.course.pk})
    
class CourseExamModel(models.Model):
    course = models.ForeignKey(CourseModel,on_delete = models.PROTECT)
    course_exams = models.ManyToManyField(Exam)
    def get_absolute_url(self):
        return reverse("details_course", kwargs={"pk": self.course.pk})



