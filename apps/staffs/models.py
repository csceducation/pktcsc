from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from apps.corecode.models import User
from django.db.models.signals import pre_delete



class Staff(models.Model):
    username = models.CharField(max_length=20,blank=False)
    password = models.CharField(max_length=20,blank=False)
    STAFF_TIMING_CHOICE = [("Full Time","Full Time"),("Part Time","Part Time")]
    STATUS = [("active", "Active"), ("inactive", "Inactive")]
    staff_roll = [("Administrative staff","Administrative staff"),("Acadamic Staff","Acadamic Staff"),('Acadamic & Administrator', 'Acadamic & Administrator'),('other', 'Other')]
    certificate_choice = [("Aadhar card","Aadhar card"),("Degree certificate","Degree certificate"),("Resume","Resume")]
    GENDER = [("male", "Male"), ("female", "Female")]
    RELIGION_CHOICE = [('Hindu','Hindu'),('Christian','Christian'),('Muslim','Muslim'),("others","others")]
    COMMUNITY_CHOICE = [('OC','OC'),('BC','BC'),('MBC','MBC'),('ST/SC','ST/SC'),("others","others")]
    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    staff_role = models.CharField("Staff Role",max_length=1024,blank=True,choices=staff_roll)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    date_of_admission = models.DateField("Date of Join",default=timezone.now)
    quali = models.CharField("Qualification",blank=True, max_length=500,null=True)
    study_year = models.IntegerField("If undergoing Year",blank=True,default=None,null=True)
    study_colleg = models.CharField("College Name",max_length=1024,blank=True)
    religion = models.CharField("Religion",max_length=554,default="Hindu",choices=RELIGION_CHOICE)
    community = models.CharField("Community",max_length=524,default="OC", choices=COMMUNITY_CHOICE)
    software_pro = models.CharField("Software Proficiency",max_length=255,blank=True)
    last_salary = models.CharField("Last Job Salary drawn",max_length=255,blank=True)
    working_exp = models.TextField("Working Experience",blank=True,null=True)
    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )
    email = models.EmailField("Email", blank=False, default="")
    
    staff_timing = models.CharField("Staff Timing",choices=STAFF_TIMING_CHOICE,default="Full Time",max_length=1023)
    address = models.CharField("Address", max_length=255,default=None,blank=True)
    address1 = models.CharField("Address Line 2", max_length=255,default=None,blank=True,null=True)
    address2 = models.CharField("Address Line 3", max_length=255,default=None,blank=True,null=True)
    taluka = models.CharField("Taluk",max_length=255,null=True,default=None,blank=True)
    district = models.CharField("District",max_length=255,default="",blank=True)
    pincode = models.IntegerField("Pincode", blank=False, default=None)
    passport = models.ImageField("Photo",blank=True, upload_to="staff/certificates/")
    aadhar_card = models.ImageField("Aadhar Card",blank=True, upload_to="staff/certificates/")
    degree_certificate = models.ImageField("Degree Certificate",blank=True, upload_to="staff/certificates/")

    resume = models.ImageField("Resume",blank=True, upload_to="staff/certificates/")
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,related_name='staff_profile')


    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})
    def age(self):
        today = datetime.now().date()
        birthdate = self.date_of_birth
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    def save(self, *args,from_save_update = True, **kwargs):
        if from_save_update:
            
            if not self.user:
                self.user = User.objects.create_user(username=self.username,password=self.password,is_staff=True)
            super().save(*args, **kwargs)
        elif not from_save_update:
            u = self.user
            self.user = None
            u.delete()
            super().save(*args, **kwargs)
    
    
    def delete(self, *args, **kwargs):
        # Delete the associated user before deleting the Staff instance
        self.save(from_save_update=False)
        super().delete(*args, **kwargs)