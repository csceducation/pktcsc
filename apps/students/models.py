from django.core.validators import RegexValidator
from datetime import datetime 
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date
from apps.course.models import CourseModel
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass , Book , Subject 
from apps.corecode.models import Time
from ..enquiry.models import *
from apps.corecode.models import User

class Student(models.Model):
    username = models.CharField(max_length=20,blank=True)
    password = models.CharField(max_length=20,blank=True)
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"),("others","others")]
    RELIGION_CHOICE = [('Hindu','Hindu'),('Christian','Christian'),('Muslim','Muslim'),("others","others")]
    COMMUNITY_CHOICE = [('OC','OC'),('BC','BC'),('MBC','MBC'),('ST/SC','ST/SC'),("others","others")]
    STUDENT_ROLE_CHOICES = [
        ("Employed", "Employed"),
        ("Unemployed", "Unemployed"),
        ("Housewife", "Housewife"),
        ("Businessman", "Businessman"),
        ("Student", "Student"),
        ("Others", "Others"),
    ]
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    if_enq = models.ForeignKey(Enquiry,on_delete=models.PROTECT,default=None,null=True)
    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    student_name = models.CharField("Student Name", max_length=255, blank=False, default="")
    enrol_no = models.IntegerField("Enrollment Number",default=0,null=False,unique=True)
    rel_name = models.CharField(
                default=None, max_length=255, verbose_name="Father/Husband Name"
            )
    rel_occupation = models.CharField("Father/Husband Occupation",max_length=255,default=None,null=False,blank=False)
    m_name = models.CharField(
                default="", max_length=255, verbose_name="Mother Name",null=True
            )
    date_of_birth = models.DateField(
                default=timezone.now, verbose_name="Date of Birth"
            )
    age = models.IntegerField("Age",default=0,blank=False)
    gender = models.CharField("Gender", max_length=10, choices=GENDER_CHOICES, default="male")
    
    religion = models.CharField("Religion",max_length=554,default="Hindu",choices=RELIGION_CHOICE)
    community = models.CharField("Community",max_length=524,default="OC", choices=COMMUNITY_CHOICE)
    occupation = models.CharField(
                choices=[
                    ("Employed", "Employed"),
                    ("Unemployed", "Unemployed"),
                    ("Housewife", "Housewife"),
                    ("Businessman", "Businessman"),
                    ("Student", "Student"),
                    ("Others", "Others"),
                ],
                default="Student",
                max_length=1024,
                verbose_name="Student Occupation",
            )
    student_company_name = models.CharField(
                blank=True,
                max_length=1024,
                null=True,
                verbose_name="If Emloyed Company Name",
            )
    
    aadhar_no = models.BigIntegerField("Aadhar Number",null=True,default=None,blank=True)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField("Mobile Number",
        validators=[mobile_num_regex], max_length=13, blank=True
    )
    email = models.EmailField("Email", blank=False, default="")
 
    #personal Details


    
    passport = models.ImageField("Photo",blank=False, upload_to="students/passports/")
    address = models.CharField("Address", max_length=255,default=None,blank=True)
    address1 = models.CharField("Address Line 2", max_length=255,default=None,blank=True,null=True)
    address2 = models.CharField("Address Line 3", max_length=255,default=None,blank=True,null=True)
    taluka = models.CharField("Taluk",max_length=255,default=None,blank=True,null=True)
    district = models.CharField("District",max_length=255,default=None,blank=True,null=True)
    pincode = models.IntegerField("Pincode", blank=True, default=None, null=True)

    #course
    date_of_admission = models.DateField(default=timezone.now)
    course = models.ForeignKey(CourseModel,on_delete=models.PROTECT)
    class_time = models.ManyToManyField(Time,verbose_name="Class Timing",blank=True)

     

    #fees

    total_fee = models.IntegerField("Total Fees",null=False,default=0)
    remark = models.CharField("Remark",max_length=500,default=None,blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,related_name='student_profile')
    
    
    class Meta:
        ordering = ["enrol_no"]

    def __str__(self):
        return f"{self.student_name}({self.enrol_no})"

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})
    


    def save(self, *args,from_save_update = True, **kwargs):
        if from_save_update:
            self.username = self.enrol_no
            self.password = self.formatted_date_of_birth()
            if not self.user:
                self.user = User.objects.create_user(username=self.enrol_no,password=self.formatted_date_of_birth(),is_staff=False)
            else:
                self.user.username = self.enrol_no
                self.user.set_password(self.formatted_date_of_birth())
                self.user.save()
            super().save(*args, **kwargs)
        elif from_save_update == False:
            self.user.delete()
            self.user = None
            super().save(*args, **kwargs)
    
    
    def delete(self, *args, **kwargs):
        # Delete the associated user before deleting the Staff instance
        self.save(from_save_update=False)
        super().delete(*args, **kwargs)
    
    def formatted_date_of_birth(self):
        # Get the date of birth
        dob = self.date_of_birth

        # Format the date as "ddmmyyyy"
        formatted_date = dob.strftime('%d%m%Y')

        return formatted_date
    
class Bookmodel(models.Model):
    student = models.ForeignKey(Student,on_delete=models.PROTECT)
    received_book = models.ForeignKey(Book , on_delete=models.CASCADE)
    received_date = models.DateField("Book received Date",default=timezone.now)
    handled_by = models.ForeignKey(Staff,verbose_name="Handled Staff",on_delete = models.DO_NOTHING)
    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.student.pk})
    remark = models.CharField("Remark",max_length=2046,blank=True,default=None)
    last_updated = models.DateTimeField(auto_now=True)
class Classmodel(models.Model):
    student = models.ForeignKey(Student,on_delete=models.PROTECT,blank=True)
    finised_subject = models.CharField("Finised Subject",max_length=255,default=None,blank=False)
    start_date = models.DateField("Started on")
    end_date = models.DateField("Ended on",null=True,blank=True)
    class_time = models.ForeignKey(Time,verbose_name="Class Timing",on_delete=models.DO_NOTHING,blank=True)
    faculty = models.ForeignKey(Staff,verbose_name="Handled Staff",on_delete = models.DO_NOTHING)
    remark = models.CharField("Remark",max_length=2046,blank=True,default=None)
    last_updated = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.student.pk})

    
class Exammodel(models.Model):
    student = models.ForeignKey(Student,on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    exam_date = models.DateField("Examed date",default=timezone.now)
    contected_mode = models.CharField("Contected mode",choices=[("Online","Online"),("Offline","Offline")],max_length=255,blank=True,null=True,default=None)
    theory_mark =models.FloatField("Theory mark",blank=True,null=True,default=None)
    paratical_mark = models.FloatField("Paratical mark",blank=True,default=None)
    mark = models.FloatField("Total mark",blank=True)
    remark = models.CharField("Remark",max_length=2046,blank=True,default=None)
    last_updated = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.student.pk})

class Certificatemodel(models.Model):
    student = models.ForeignKey(Student,on_delete=models.PROTECT)
    course = models.ForeignKey(CourseModel,on_delete=models.CASCADE)
    date_of_complete = models.DateField("Date of Completion",default=timezone.now)
    certificate_no = models.IntegerField("Certificate Number",default=None,blank=True)
    certificate_date = models.DateField("Certificate Date",default=timezone.now)
    certificate_issued_date = models.DateField("Certificate Issued Date",default=timezone.now)
    grade = models.CharField("Grade on Certificate",max_length=10,blank=True,default=None)
    issued_by = models.ForeignKey(Staff,verbose_name ="Certificate Issued By",on_delete = models.DO_NOTHING)
    remark = models.CharField("Remark",max_length=2046,blank=True,default=None)
    last_updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.student.pk})

    
    
    
    
    
    
    
    
    
    
    
    
    """ 
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    registration_number = models.CharField(max_length=200, unique=True)
    surname = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    other_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(
        StudentClass, on_delete=models.SET_NULL, blank=True, null=True
    )
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    parent_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")

    class Meta:
        ordering = ["surname", "firstname", "other_name"]

    def __str__(self):
        return f"{self.surname} {self.firstname} {self.other_name} ({self.registration_number})"

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})

 """
class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")
