from django.db import models
from apps.course.models import CourseModel
from apps.corecode.models import Subject
from apps.staffs.models import Staff
from apps.students.models import Student
from django.utils import timezone
from django.urls import reverse
from apps.corecode.models import Time
from apps.attendancev2.manager import AttendanceManager
from csc_app.settings import db

class BatchModel(models.Model):
    batch_status = models.CharField("Batch Status", max_length=255, choices=[("Active", "Active"), ("Inactive", "Inactive")])
    batch_id = models.CharField("Batch Id", max_length=255, blank=True)
    batch_course = models.ForeignKey(Subject, verbose_name="Batch subject", on_delete=models.PROTECT)
    batch_staff = models.ForeignKey(Staff, on_delete=models.PROTECT,limit_choices_to={'current_status': 'active'})
    batch_students = models.ManyToManyField(Student, blank=True,limit_choices_to={'current_status': 'active'})
    batch_start_date = models.DateField("Batch Start Date", default=timezone.now)
    batch_end_date = models.DateField("Batch End Date", default=None, blank=True, null=True)
    batch_timing = models.ForeignKey(Time, verbose_name="Class Timing", on_delete=models.DO_NOTHING, blank=True)

    def total_student(self):
        return self.batch_students.count()

    def get_batch_name(self):
        return str(self.batch_id) + str(self.batch_course)
    def get_absolute_url(self):
        return reverse("batch_detail", kwargs={"pk": self.pk})
    
    @property
    def is_active(self):
        return self.batch_status == "Active"

    def calculate_duration(self):
        return (self.batch_end_date - self.batch_start_date).days

    

    class Meta:
        ordering = ["-batch_start_date"]

    def initialize_batch_attendance(self, date, content, entry_time, exit_time):
        manager = AttendanceManager(db)
        manager.initialize_batch(self.id, date, content, entry_time, exit_time, self.get_students())

    def get_students(self):
        students = {}
        for student in self.batch_students.all():
            students[str(student.enrol_no)] = "present"
        return students
        
    @staticmethod
    def map_name(enrol_no):
        student = Student.objects.get(enrol_no=enrol_no)
        return student.student_name

    def add_theory_attendance(self, content,entry_time,exit_time,student, status, date):
        manager = AttendanceManager(db)
        manager.add_theory_attendance(self.id, student, date, status,content,entry_time,exit_time)
        
    
    def get_attendance_data(self, date):
        manager = AttendanceManager(db)
        doc = manager.get_theory_data(self.id, date)
        if doc:
            for enrol_no, status in doc['students'].items():
                doc['students'][enrol_no] = {
                    'name': self.map_name(enrol_no),
                    'status': status
                }
            #print(doc)
            return doc

    def finished_topics(self):
        manager = AttendanceManager(db)
        doc = manager.get_all_theory_data(self.id)
        finished = []
        #print(doc)
        for data in doc:
            print(data['content'])
            finished.extend(data['content'])
        #print(finished)
        return finished