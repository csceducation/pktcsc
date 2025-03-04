from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
import re
from collections import defaultdict
class User(AbstractUser):
    notes = models.TextField(blank=True, null=True)
    #staff = models.ForeignKey('staffs.Staff',on_delete=models.CASCADE,null=True,blank=True)
    #student = models.ForeignKey('students.Student',on_delete=models.CASCADE,null=True,blank=True)
    

class SiteConfig(models.Model):
    """Site Configurations"""

    key = models.SlugField()
    value = models.CharField(max_length=200)

    def __str__(self):
        return self.key


class AcademicSession(models.Model):
    """Academic Session"""

    name = models.CharField(max_length=200, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic Term"""

    name = models.CharField(max_length=20, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Subject"""

    name = models.CharField(max_length=200, unique=True)
    duration = models.CharField("Duration (*In Hours)",max_length=200,blank=True)
    contents = models.TextField("Content (*Enter line by line)",blank=True, null=True)
    
    def get_day_contents(self):
        cont_list = self.contents.splitlines()
        contents = {}
        for i in range(len(cont_list)):
            contents[f"day-{i+1}"]  = cont_list[i]
        #print(contents)
        return contents 
    def get_contents(self):
        return self.contents.splitlines()
        
    def calculate_duration(self):
        return self.extract_number(self.duration)
    
    def extract_number(self,text):
        # Use a regular expression to find the first number in the text
        match = re.search(r'\d+', text)
        # If a match is found, convert it to an integer and return it
        return int(match.group()) if match else 0
        
        
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
class Book(models.Model):
    """Book"""

    name = models.CharField(max_length=200, unique=True,blank=True)
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
class Time(models.Model):
    """Timing"""

    time = models.CharField(max_length=200,blank=True)

    class Meta:
        ordering = ["time"]

    def __str__(self):
        return self.time
class Exam(models.Model):
    """Exam"""

    name = models.CharField(max_length=200, unique=True,blank=True)
    subject = models.OneToOneField(Subject,on_delete=models.PROTECT,null=True)
    exam_mode = models.CharField(max_length=255,choices=[("Online","online"),("Offline","Offline")],default="Offline")
    exam_duration = models.CharField("Exam Duration (In  Minutes)",max_length=200,blank=True)
    max_theory_marks = models.IntegerField(blank=False,null=False)
    max_practical_marks = models.IntegerField(blank=False,null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def max_total_marks(self):
        return self.max_practical_marks+self.max_theory_marks
    
class StudentClass(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Bill(models.Model):
    prefix = models.CharField(max_length=45,blank=False, null=False)
    last_bill = models.IntegerField(blank=False, null=False)
class AccountHeading(models.Model):
    """Account Heading"""

    name = models.CharField(max_length=260, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Schemes(models.Model):
    """Scheme Lists"""
    scheme_status = models.CharField(max_length=200,blank=True,choices=(("Active","Active"),("Inactive","Inactive")))
    name = models.CharField(max_length=260, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    class Meta:
        ordering = ["scheme_status", "name"]

    def __str__(self):
        return self.name


class Inventory(models.Model):
    order_id = models.CharField(max_length=50, unique=True)  # Order reference
    order_date = models.DateField()  

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,limit_choices_to={
        'model__in':['book','schemes']
    })

    items = models.JSONField(default=dict)

    def books_stock(self):
        print("hello")
        stock_levels = defaultdict(int)
        orders = Inventory.objects.filter(order_date__gt="2025-01-28")
        for order in orders:
            for book_id, quantity in order.items.items():
                stock_levels[int(book_id)] += quantity
        return dict(stock_levels)
        
    def book_stock(self,book_id):
        orders = Inventory.objects.filter(order_date__gt="2025-01-28")
        ord = [{"order":order.order_id,'id':order.id,'stock':order.items[str(book_id)]} for order in orders if str(book_id) in order.items]
        total_stock = sum(list(map(lambda x:x['stock'],ord)))
        return ord,total_stock
    
    def __str__(self):
        return f"Order {self.order_id} - {self.content_type} ({self.order_date})"