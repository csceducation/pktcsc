from django.shortcuts import render,redirect,reverse
from django.http import HttpResponseRedirect
import json,random
from datetime import datetime
from .models import LabSystemModel
from .manager import AttendanceManager,DailyAttendanceManager
from .dashboard import DashboardManager
from apps.students.models import Student
from apps.staffs.models import Staff
from datetime import datetime,timedelta
import plotly.express as px
from apps.batch.models import BatchModel
from .froms import DateForm
from csc_app.settings import db

def create_labs(request):
    if request.method == "POST":
        lab_no = request.POST.get("lab_no")
        labmodel,created = LabSystemModel.objects.get_or_create(lab_no=lab_no)
        if labmodel:
            labmodel.save()
        else:
            created.save()
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

    
def labs(request):
    labs = LabSystemModel.objects.all()
    return render(request,"labs_list.html",{"labs":labs})


def add_systems(request,**kwargs):
    lab = LabSystemModel.objects.get(id=kwargs.get("lab_id"))
    
    system_name = request.POST.get("system_name")
    
    lab.append_system(system_name)

    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_system(request,**kwargs):
    lab = LabSystemModel.objects.get(id=kwargs.get("lab_id"))
    system_name = kwargs.get('system_name')
    lab.delete_system(system_name)
    lab.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def lab_details(request,**kwargs):
    lab = LabSystemModel.objects.get(id=kwargs.get("lab_id"))

    return render(request,"batch_detail.html",{"lab":lab})


def delete_lab(request,**kwargs):
    lab = LabSystemModel.objects.get(id=kwargs.get("lab_id"))
    lab.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))
    

    
def add_lab_attendance(request, **kwargs):
    lab_id = int(kwargs.get('lab_id'))
    date = request.GET.get("date")

    if not date:
        return render(request, "date_form.html")

    manager = AttendanceManager(db)

    if request.method == "POST":
        system_no = request.POST.get("system_no")
        student = request.POST.get("enrol_no")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        manager.put_lab_collection(lab_id, system_no, student, start_time, end_time, date)

        return redirect(request.META.get('HTTP_REFERER', '/'))

    lab = LabSystemModel.objects.get(id=int(lab_id))
    systems = lab.get_systems()
    data = lab.get_attendance_data(date)

    students = Student.objects.filter(current_status="active")
    students_id = [{"id": student.enrol_no, "name": student.student_name} for student in students]
    context = {
        "system_data_dict": data, 
        "students": students_id, 
        "systems": systems,
        "lab_no":lab_id,
        "date":date
    }
    return render(request, "lab_attendance.html", context)


def delete_lab_attendance_data(request,**kwargs):
    lab_no = kwargs.get("lab_id")
    system_no = kwargs.get("system_no")
    date = kwargs.get("date")
    student_id = kwargs.get("student_id")

    manager = AttendanceManager(db)
    manager.delete_lab_data(lab_no,system_no,student_id,date)
    del manager

    return redirect(request.META.get('HTTP_REFERER', '/'))


def get_key(key,val,finished):
    for value in finished:
        if val == value:
            return True
        else:
            False

def add_theory_attendance(request,batch_id):
    batch = BatchModel.objects.get(id=batch_id)
    
    if 'date' in request.GET:
        date = request.GET.get('date')
    else:
        if request.method == 'POST':
            
            date = request.POST['date']
            content =""
            entry_time = ""
            exit_time = ""
            batch.initialize_batch_attendance(date,content,entry_time,exit_time)
            return HttpResponseRedirect(request.path + f"?date={date}&entrytime={entry_time}&exittime={exit_time}")
        else:
            form = DateForm()
        return render(request, 'theory_date_form.html', {'form': form})

    
    if request.method == 'POST':
        #content = request.POST.get('content')
        content = request.POST.getlist('content')
        entry_time = request.POST.get('entrytime')
        exit_time = request.POST.get('exittime')
        students_present = request.POST.getlist('students')
        for student in batch.batch_students.all():
            print(students_present)
            status = "present" if str(student.enrol_no) in students_present else "absent"
            batch.add_theory_attendance(content,entry_time,exit_time,student.enrol_no,status,date)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    existing_data = batch.get_attendance_data(date)
    """
    #for the previous without day contents
    contents_to_include = batch.batch_course.contents
    contents_list = contents_to_include.splitlines()
    removed = sorted(list(set(contents_list)-set(batch.finished_topics())))
    """
    contents = batch.batch_course.get_day_contents()
    #print(contents)
    finished_topics = batch.finished_topics()
    removed = [key  for key, value in contents.items() if get_key(key,value,finished_topics)  ]
    print(removed)
    return render(request,"theory_attendance_form.html",{"data":existing_data,"batch":batch,"contents":removed,"org_contents":contents})


def delete_theory_attendance(request,**kwargs):
    batch_id = kwargs.get("batch_id","")
    date = kwargs.get("date","")
    student_id = kwargs.get("stud_id")
    manager = AttendanceManager(db)
    manager.delete_attendance(batch_id=batch_id,date=date,student_id=student_id)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def staff_attendance(request):
    manager = DailyAttendanceManager(db)

    if 'date' in request.GET:
        date = request.GET.get('date')
    else:
        if request.method == 'POST':
            form = DateForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                return HttpResponseRedirect(request.path + f"?date={date}")
        else:
            form = DateForm()
        return render(request, 'date_form.html', {'form': form})

    manager.initialize_staff(date)
    existing_data = manager.get_staff_attendance(date)
    staff_queryset = Staff.objects.all()
    if request.method == 'POST':
        for staff in staff_queryset:
            student_id = staff.id
            entry_time = request.POST.get(f'entry_time_{staff.id}')
            exit_time = request.POST.get(f'exit_time_{staff.id}')
            status = request.POST.get(f"status_{staff.id}")
            
            manager.add_staff_attendance(student_id, date, entry_time, exit_time,status)

        redirect_url = reverse('staff_attendance') + f'?date={date}'
        return HttpResponseRedirect(redirect_url)

    staffs_data = []
    
    
    for staff in staff_queryset:
        staffs_data.append({
            'staff_id': staff.id,
            'name': staff.username,
            'entry_time': existing_data.get(str(staff.id), {}).get("entry_time", ""),
            'exit_time': existing_data.get(str(staff.id), {}).get("exit_time", ""),
            'status':existing_data.get(str(staff.id),{}).get('status',"")
        })

    context = {
        'date': date,
        'staffs_data': staffs_data,
    }

    return render(request, 'staff_attendance.html', context)


def delete_staff_attendance(request,**kwargs):
    date = kwargs.get("date","")
    staff_id = kwargs.get("staff_id","")
    manager = DailyAttendanceManager(db)
    manager.delete_staff_attendance(date,str(staff_id))
    return redirect(request.META.get('HTTP_REFERER', '/'))

def student_attendance(request):
    manager = DailyAttendanceManager(db)

    if 'date' in request.GET:
        date = request.GET.get('date')
    else:
        if request.method == 'POST':
            form = DateForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                return HttpResponseRedirect(request.path + f"?date={date}")
        else:
            form = DateForm()
        return render(request, 'date_form.html', {'form': form})

    manager.initialize_student(date)
    existing_data = manager.get_student_attendance(date)
    student_queryset = Student.objects.all()
    if request.method == 'POST':
        for student in student_queryset:
            student_id = student.id
            entry_time = request.POST.get(f'entry_time_{student.id}')
            exit_time = request.POST.get(f'exit_time_{student.id}')
            status = request.POST.get(f"status_{student.id}")
            
            manager.add_student_attendance(student_id, date, entry_time, exit_time,status)

        redirect_url = reverse('student_attendance') + f'?date={date}'
        return HttpResponseRedirect(redirect_url)

    students_data = []
    
    
    for student in student_queryset:
        students_data.append({
            'student_id': student.id,
            'name': student.student_name,
            'entry_time': existing_data.get(str(student.id), {}).get("entry_time", ""),
            'exit_time': existing_data.get(str(student.id), {}).get("exit_time", ""),
            'status': existing_data.get(str(student.id), {}).get("status", "")
        })

    context = {
        'date': date,
        'students_data': students_data,
    }

    return render(request, 'student_attendance.html', context)

def delete_student_attendance(request,**kwargs):
    date = kwargs.get("date","")
    student_id = kwargs.get("student_id","")
    manager = DailyAttendanceManager(db)
    manager.delete_student_attendance(date,str(student_id))
    return redirect(request.META.get('HTTP_REFERER', '/'))


def router(request):
    return render(request,'router.html')

def day_dashboard(request, *args):
    selected_week = request.GET.get('week')
    date = request.GET.get('date')

    if selected_week:
        year, week_num = map(int, selected_week.split('-W'))
        first_day_of_week = datetime.strptime(f'{year}-W{week_num}-1', "%Y-W%W-%w")
    else:
        # If 'week' parameter is not provided, use the current week
        today = datetime.now()
        year, week_num, _ = today.isocalendar()
        first_day_of_week = today - timedelta(days=today.weekday())  # Start of the current week

    dates = []
    for i in range(7):
        day = first_day_of_week + timedelta(days=i)
        if day.weekday() != 6:
            dates.append(day.strftime('%Y-%m-%d'))  # Format date as 'yy-mm-dd'

    if date is None:
        date = dates[0]

    manager = DashboardManager(db)
    staff_strength, staff_presentees = manager.get_staff_attendance(dates)
    student_strength, students_presentees = manager.get_student_attendance(dates)

    students_data = manager.get_student_table(date)
    staffs_data = manager.get_staff_table(date)

    
    staff_trace1 = {
        'x': dates,
        'y': [item[1] for item in staff_presentees],
        'name': 'Staff Presentees',
        'type': 'bar'
    }
    staff_trace2 = {
        'x': dates,
        'y': [staff_strength for _ in range(len(dates))],
        'name': 'Staff Strength',
        'type': 'bar'
    }
    staff_data = [staff_trace1, staff_trace2]
    staff_layout = {
        'title': 'Staff Attendance',
        'barmode': 'group'
    }
    staff_fig = {
        'data': staff_data,
        'layout': staff_layout
    }

    # Create the bar chart for students
    student_trace1 = {
        'x': dates,
        'y': [item[1] for item in students_presentees],
        'name': 'Student Presentees',
        'type': 'bar'
    }
    student_trace2 = {
        'x': dates,
        'y': [student_strength for _ in range(len(dates))],
        'name': 'Student Strength',
        'type': 'bar'
    }
    student_data = [student_trace1, student_trace2]
    student_layout = {
        'title': 'Student Attendance',
        'barmode': 'group'
    }
    student_fig = {
        'data': student_data,
        'layout': student_layout
    }
    staff_graphJSON = json.dumps(staff_fig)
    student_graphJSON = json.dumps(student_fig)
    context = {
        'students_data': students_data,
        'staffs_data': staffs_data,
        'week_dates': dates,
        'staff_graphJSON': staff_graphJSON,
        'student_graphJSON': student_graphJSON,

    }
    return render(request, 'day_dashboard.html', context)
    

def provide_staff_summary(staff,month,year):
    manager = DashboardManager(db)
    data = manager.get_staff_summary(staff,month,year)
    #print(data)
    return data


def lab_dashboard(request,lab_id):
    date = request.GET.get("date")
    if date == None:
        date = datetime.today()
        
    lab = LabSystemModel.objects.get(id=lab_id)
    systems = lab.get_systems()
    data = lab.get_attendance_data(date)
    time_slots = [f'{h:02d}:{m:02d}' for h in range(0, 24) for m in (0, 30)]

    students = Student.objects.filter(current_status="active")
    students_id = [{"id": student.enrol_no, "name": student.student_name} for student in students]
    context = {
        "system_data_dict": data, 
        "students": students_id, 
        "systems": systems,
        "lab_no":lab_id,
        "date":date,
        'time_slots': time_slots,
    }
    student_id = request.GET.get('student_id')
    week = request.GET.get('week')
    if student_id != None and week != None:
        student = Student.objects.get(enrol_no=student_id)
        manager = AttendanceManager(db)
        context["student_data"] = manager.get_student_lab_data(str(student.enrol_no),week)
        return render(request,"lab_dashboard.html",context) 
        
        
    return render(request,"lab_dashboard.html",context) 

def theory_dashboard(request):
    staff_id = request.GET.get("staff_id")
    staffs = Staff.objects.all()
    staff_list = [{"id":s.id,"name":s.username} for s in staffs]
    if not staff_id:
        return render(request,'theory_dashboard_form.html',{'staff_list':staff_list})
    batch_id = request.GET.get("batch")
    date = request.GET.get("date")
    staff = Staff.objects.get(id=int(staff_id))
    
    staff_list = [{"id":s.id,"name":s.username} for s in staffs]
    batches = BatchModel.objects.filter(batch_staff = staff)
    manager = AttendanceManager(db)
    result = {}
    for batch in batches:
        data = manager.get_theory_dashboard(batch.id)
        result[batch.get_batch_name()] = data
    
        
    all_batches = BatchModel.objects.all()
    batch_list = [{"id":b.id,'name':b.get_batch_name()} for b in batches]
    context = {
        "data_for_staff":result,
        "staff_list":staff_list,
        "batch_list":batch_list,
    }
    #print(context)
    if batch_id and date:
        
        doc = manager.get_theory_data(int(batch_id),date)
        if doc :
            doc.pop('_id', None)
            students = doc.get('students', {})
            mapped_students = {student_id: {'name': map_name(student_id), 'status': status} for student_id, status in students.items()}
            doc['students'] = mapped_students

            context['specific_date'] = doc
        
    return render(request,"theory_dashboard.html",context)
    

def map_name(enrol_no):
    try:
        student = Student.objects.get(enrol_no=enrol_no)
        return student.student_name
    except:
        return "unknown"
    
    
def profile_redirector(request,**kwargs):
    enrol_no = kwargs.get("enrol_no")
    
    student = Student.objects.get(enrol_no=enrol_no)
    return redirect('public_student_profile',student.id)