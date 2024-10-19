import os
import django
import random
from faker import Faker
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csc_app.settings')
django.setup()

from apps.enquiry.models import Enquiry
from apps.staffs.models import Staff
from apps.corecode.models import Time
from apps.course.models import CourseModel
fake = Faker()

def create_fake_enquiry():
    # Assuming you have some Staff and CourseModel objects already created
    staff = Staff.objects.filter().first()
    course = CourseModel.objects.filter().first()

    enquiry = Enquiry.objects.create(
        enquiry_no=fake.unique.bothify(text='ENQ####'),
        name=fake.name(),
        f_name=fake.name_male() if fake.boolean() else fake.name_female(),
        address=fake.address(),
        address1=fake.secondary_address(),
        address2=fake.secondary_address(),
        taluka=fake.city(),
        district=fake.state(),
        pincode=fake.postcode(),
        mobile_number=fake.phone_number(),
        alternate_mobile_number=fake.phone_number(),
        email=fake.email(),
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
        gender=random.choice([choice[0] for choice in Enquiry.GENDER_CHOICES]),
        student_role=random.choice([choice[0] for choice in Enquiry.STUDENT_ROLE_CHOICES]),
        student_company_name=fake.company() if random.choice([True, False]) else None,
        enquiry_date=fake.date_this_year(),
        counsellor=staff,
        counsellor_remark=fake.text(),
        enquiry_status="Following",
        expected_date=fake.date_this_year(),
        qualification=fake.text(max_nb_chars=50),
        qualification_status=random.choice([choice[0] for choice in Enquiry.QUALIFICATION_STATUS_CHOICES]),
        studying_year=fake.random_int(min=1, max=5),
        studying_course=fake.job(),
        student_college_name=fake.company(),
        need_of_study=random.choice([choice[0] for choice in Enquiry.NEED_CHOICES]),
        known_csc=random.choice([choice[0] for choice in Enquiry.KNOWN_CSC_CHOICES]),
        course_to_join=course,
        new_course=fake.word()
    )

    # Add many-to-many field values
    #times = Time.objects.get(id=1)
    #enquiry.time_to_study.set(times)

    enquiry.save()

# Create multiple fake enquiries
for _ in range(10):
    create_fake_enquiry()
