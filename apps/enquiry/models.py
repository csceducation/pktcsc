from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date
from apps.staffs.models import Staff
from apps.corecode.models import Time
from apps.course.models import CourseModel


class Enquiry(models.Model):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"),("others","others")]
    QUALIFICATION_STATUS_CHOICES = [("Completed", "Completed"), ("Undergoing", "Undergoing"),("others","others")]
    STUDENT_ROLE_CHOICES = [
        ("Employed", "Employed"),
        ("Unemployed", "Unemployed"),
        ("Housewife", "Housewife"),
        ("Businessman", "Businessman"),
        ("Student", "Student"),
        ("Others", "Others"),
    ]
    NEED_CHOICES = [
        ("For a job", "For a job"),
        ("For a job in software profession", "For a job in software profession"),
        ("For advance study", "For advance study"),
        ("Sponsored by company", "Sponsored by company"),
        ("others","others")
    ]
    KNOWN_CSC_CHOICES = [
        ("Television", "Television"),
        ("Newspaper", "Newspaper"),
        ("Friend recommend", "Friend recommend"),
        ("Poster", "Poster"),
        ("others","others")
    ]
    ENQUIRY_STATUS_CHOICES = [
        ("Following", "Following"),
        ("Admitted", "Admitted"),
        ("Rejected", "Rejected"),
    ]

    auto_increment = models.AutoField(primary_key=True)
    enquiry_no = models.CharField("Enquiry Number", max_length=20, unique=True, editable=False)
    name = models.CharField("Name", max_length=255, blank=False, default="")
    f_name = models.CharField("Father Name", max_length=255, blank=False, default="")
    m_name = models.CharField("Mother Name", max_length=255, blank=False, default="")
    address = models.CharField("Address", max_length=255,default=None,blank=False)
    address1 = models.CharField("Address Line 2", max_length=255,default=None,blank=True,null=True)
    address2 = models.CharField("Address Line 3", max_length=255,default=None,blank=True,null=True)
    taluka = models.CharField("Taluk",max_length=255,null=True,default=None,blank=True)
    district = models.CharField("District",max_length=255,default="",blank=False)
    pincode = models.IntegerField("Pincode", blank=True, default=None,null=True)
    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField("Mobile Number",
        validators=[mobile_num_regex], max_length=13, blank=True , null=True
    )#null = False 
    alternate_mobile_number = models.CharField("Alternate Mobile Number",
        validators=[mobile_num_regex], max_length=13, blank=True , null=True
    )
    email = models.EmailField("Email", blank=True, default="" ,null=True)
    date_of_birth = models.DateField("Date of Birth",default=timezone.now)
    gender = models.CharField("Gender", max_length=10, choices=GENDER_CHOICES, default="male")
    student_role = models.CharField(
        "Occupation", choices=STUDENT_ROLE_CHOICES, max_length=1024, default="Student"
    )
    student_company_name = models.CharField("If Emloyed Company Name",max_length=1024,blank=True,null=True)
    
    # Office Use
    enquiry_date = models.DateField(default=timezone.now)
    counsellor = models.ForeignKey(Staff,on_delete=models.DO_NOTHING,limit_choices_to={'current_status': 'active'},default=None)
    counsellor_remark = models.TextField("Counsellor Remark", default="",null=True)
    enquiry_status = models.CharField(
        "Enquiry Status", choices=ENQUIRY_STATUS_CHOICES, max_length=1024, default="Following"
    )
    expected_date = models.DateField("Expected Date of Join",default=timezone.now)
    # Otherse
    qualification = models.TextField("Qualification", blank=False, default="",null=False)
    qualification_status = models.CharField(
        "Qualification Status", max_length=50, choices=QUALIFICATION_STATUS_CHOICES, default="Completed",blank =True,null=True
    )
    studying_year = models.IntegerField("Current year",default=None,null=True,blank=True)
    studying_course = models.TextField("Major", max_length=255, default="",blank=True)
    student_college_name = models.CharField("School/College Name",max_length=1055,default="",blank=True,null=True)

    #others
    need_of_study = models.CharField(
        "Reason for Study", max_length=1024, choices=NEED_CHOICES, default="For a job"
    )
    known_csc = models.CharField(
        "How You Know about CSC", choices=KNOWN_CSC_CHOICES, default="Newspaper", max_length=1024
    )
    course_to_join = models.ForeignKey(CourseModel,on_delete=models.CASCADE,blank=True,null=True)
    new_course = models.CharField(
        "Others", max_length=1024, default="",blank=True,null=True
    )
    time_to_study = models.ManyToManyField(Time,blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            last_student = Enquiry.objects.order_by('-auto_increment').first()
            last_auto_increment = last_student.auto_increment if last_student else 0
            self.enquiry_no = f'EN24-{last_auto_increment + 1:04d}'
        
        super().save(*args, **kwargs)
        return self.enquiry_no
    def __str__(self):
        return f"{self.enquiry_no}"
    
    # Properties for organization
    @property
    def personal_info(self):
        return {
            "name": self.name,
            "address": self.address,
            "pincode": self.pincode,
            "mobile_number": self.mobile_number,
            "email": self.email,
            "gender": self.gender,
            "taluka":self.taluka,
            "district":self.district
        }
        
    @property
    def office_use(self):
        return {
            "enquiry_date": self.enquiry_date,
            "counsellor_remark": self.counsellor_remark,
            "enquiry_status": self.enquiry_status,
        }

    @property
    def others(self):
        return {
            "qualification": self.qualification,
            "qualification_status": self.qualification_status,
            "studying_year": self.studying_year,
            "studying_course": self.studying_course,
            "student_role": self.student_role,
            "need_of_study": self.need_of_study,
            "course_to_join": self.course_to_join,
            "time_to_study": self.time_to_study,
            "known_csc": self.known_csc,
        }
    def get_absolute_url(self):
        return reverse("enquiry-detail", kwargs={"pk": self.pk})
    
    
    @property
    def age(self):
        today = date.today()
        birth_date = self.date_of_birth
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def formatted_date_of_birth(self):
        # Get the date of birth
        dob = self.date_of_birth

        # Format the date as "ddmmyyyy"
        formatted_date = dob.strftime('%d%m%Y')

        return formatted_date
    
    
        
        

        
class Enquirylogs(models.Model):
    contact_choice = [("Phone","Phone"),("Whatsapp","Whatsapp"),("Email","Email")]
    student = models.ForeignKey(Enquiry,on_delete=models.PROTECT)
    staff_contact = models.ForeignKey(Staff,on_delete=models.DO_NOTHING)
    exp_date = models.DateField("Expected date",default=timezone.now)
    contact_by = models.CharField("Contact By",max_length=255,choices=contact_choice,default="Phone")
    log_date = models.DateField("Enquired Date",default=timezone.now)
    comment = models.TextField("Remark",default=None,blank=True,null=True)
    def get_absolute_url(self):
        return reverse("enquiry-detail", kwargs={"pk": self.student.pk})
    def __str__(self):
        return f"{self.student.enquiry_no}"
    
class StudentEnquiryModel(models.Model):
        GENDER_CHOICES = [("male", "Male"), ("female", "Female"),("others","others")]
        QUALIFICATION_STATUS_CHOICES = [("Completed", "Completed"), ("Undergoing", "Undergoing"),("others","others")]
        STUDENT_ROLE_CHOICES = [
            ("Employed", "Employed"),
            ("Unemployed", "Unemployed"),
            ("Housewife", "Housewife"),
            ("Businessman", "Businessman"),
            ("Student", "Student"),
            ("Others", "Others"),
        ]
        NEED_CHOICES = [
            ("For a job", "For a job"),
            ("For a job in software profession", "For a job in software profession"),
            ("For advance study", "For advance study"),
            ("Sponsored by company", "Sponsored by company"),
            ("others","others")
        ]
        KNOWN_CSC_CHOICES = [
            ("Television", "Television"),
            ("Newspaper", "Newspaper"),
            ("Friend recommend", "Friend recommend"),
            ("Poster", "Poster"),
            ("others","others")
        ]
        ENQUIRY_STATUS_CHOICES = [
            ("Following", "Following"),
            ("Admitted", "Admitted"),
            ("Rejected", "Rejected"),
        ]

        auto_increment = models.AutoField(primary_key=True)
        enquiry_no = models.CharField("Enquiry Number", max_length=20, unique=True, editable=False)
        name = models.CharField("Name", max_length=255, blank=False, default="")
        f_name = models.CharField("Father Name", max_length=255, blank=False, default="")
        m_name = models.CharField("Mother Name", max_length=255, blank=False, default="")
        address = models.CharField("Address", max_length=255,default=None,blank=False)
        address1 = models.CharField("Address Line 2", max_length=255,default=None,blank=True,null=True)
        address2 = models.CharField("Address Line 3", max_length=255,default=None,blank=True,null=True)
        taluka = models.CharField("Taluk",max_length=255,null=True,default=None,blank=True)
        district = models.CharField("District",max_length=255,default="",blank=False)
        pincode = models.IntegerField("Pincode", blank=True, default=None,null=True)
        mobile_num_regex = RegexValidator(
            regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
        )
        mobile_number = models.CharField("Mobile Number",
            validators=[mobile_num_regex], max_length=13, blank=True , null=True
        )
        alternate_mobile_number = models.CharField("Alternate Mobile Number",
            validators=[mobile_num_regex], max_length=13, blank=True , null=True
        )
        email = models.EmailField("Email", blank=True, default="" ,null=True)
        date_of_birth = models.DateField("Date of Birth",default=timezone.now)
        gender = models.CharField("Gender", max_length=10, choices=GENDER_CHOICES, default="male")
        student_role = models.CharField(
            "Occupation", choices=STUDENT_ROLE_CHOICES, max_length=1024, default="Student"
        )
        student_company_name = models.CharField("If Emloyed Company Name",max_length=1024,blank=True,null=True)
        
        # Others
        qualification = models.TextField("Qualification", blank=True, default="",null=True)
        qualification_status = models.CharField(
            "Qualification Status", max_length=50, choices=QUALIFICATION_STATUS_CHOICES, default="Completed"
        )
        studying_year = models.IntegerField("Current year",default=None,null=True,blank=True)
        studying_course = models.TextField("Major", max_length=255, default="",blank=True,null=True)
        student_college_name = models.CharField("School/College Name",max_length=1055,default="",blank=True,null=True)

        #others
        need_of_study = models.CharField(
            "Reason for Study", max_length=1024, choices=NEED_CHOICES, default="For a job"
        )
        known_csc = models.CharField(
            "How You Know about CSC", choices=KNOWN_CSC_CHOICES, default="Newspaper", max_length=1024
        )
        course_to_join = models.ForeignKey(CourseModel,on_delete=models.CASCADE,blank=True,null=True)
        new_course = models.CharField(
            "Others", max_length=1024, default="",blank=True,null=True
        )
        time_to_study = models.ManyToManyField(Time,blank=True)
        enquiry_date = models.DateField(default=timezone.now,blank=True)
        verfied = models.BooleanField(default=False)

        
        def save(self, *args, **kwargs):
            if not self.pk:
                last_student = StudentEnquiryModel.objects.order_by('-auto_increment').first()
                last_auto_increment = last_student.auto_increment if last_student else 0
                self.enquiry_no = f'EN24-{last_auto_increment + 1:04d}'
            
            super().save(*args, **kwargs)
            return self.enquiry_no
        def __str__(self):
            return f"{self.enquiry_no}"
        
        # Properties for organization
        @property
        def personal_info(self):
            return {
                "name": self.name,
                "address": self.address,
                "pincode": self.pincode,
                "mobile_number": self.mobile_number,
                "email": self.email,
                "gender": self.gender,
                "taluka":self.taluka,
                "district":self.district
            }
            

        @property
        def others(self):
            return {
                "qualification": self.qualification,
                "qualification_status": self.qualification_status,
                "studying_year": self.studying_year,
                "studying_course": self.studying_course,
                "student_role": self.student_role,
                "need_of_study": self.need_of_study,
                "course_to_join": self.course_to_join,
                "time_to_study": self.time_to_study,
                "known_csc": self.known_csc,
            }
        def get_absolute_url(self):
            return reverse("pending-enquiry-list")
        
        
        @property
        def age(self):
            today = date.today()
            birth_date = self.date_of_birth
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age

        def formatted_date_of_birth(self):
            # Get the date of birth
            dob = self.date_of_birth

            # Format the date as "ddmmyyyy"
            formatted_date = dob.strftime('%d%m%Y')

            return formatted_date