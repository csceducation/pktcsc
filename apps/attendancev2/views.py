from django.shortcuts import render,redirect,reverse
from django.http import HttpResponseRedirect,JsonResponse,HttpResponse
import json,random
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import LabSystemModel
from .manager import AttendanceManager,DailyAttendanceManager,AttendanceManagerV2
from .dashboard import DashboardManager
from apps.students.models import Student
from apps.staffs.models import Staff
from datetime import datetime,timedelta
import plotly.express as px
from apps.batch.models import BatchModel
from .froms import DateForm
from csc_app.settings import db
from apps.corecode.utils import debug_info
import ast
from .analaytics import AnalyticManager
from datetime import date

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

    return render(request,"lab_detail.html",{"lab":lab})


def delete_lab(request,**kwargs):
    lab = LabSystemModel.objects.get(id=kwargs.get("lab_id"))
    lab.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))
    

    
# def add_lab_attendance(request, **kwargs):
#     lab_id = int(kwargs.get('lab_id'))
#     date = request.GET.get("date")

#     if not date:
#         return render(request, "date_form.html")

#     manager = AttendanceManager(db)

#     if request.method == "POST":
#         system_no = request.POST.get("system_no")
#         student = request.POST.get("enrol_no")
#         start_time = request.POST.get("start_time")
#         end_time = request.POST.get("end_time")
#         manager.put_lab_collection(lab_id, system_no, student, start_time, end_time, date)

#         return redirect(request.META.get('HTTP_REFERER', '/'))

#     lab = LabSystemModel.objects.get(id=int(lab_id))
#     systems = lab.get_systems()
#     data = lab.get_attendance_data(date)

#     students = Student.objects.filter(current_status="active")
#     students_id = [{"id": student.enrol_no, "name": student.student_name} for student in students]
#     context = {
#         "system_data_dict": data, 
#         "students": students_id, 
#         "systems": systems,
#         "lab_no":lab_id,
#         "date":date
#     }
#     return render(request, "lab_attendance.html", context)


# def delete_lab_attendance_data(request,**kwargs):
#     lab_no = kwargs.get("lab_id")
#     system_no = kwargs.get("system_no")
#     date = kwargs.get("date")
#     student_id = kwargs.get("student_id")

#     manager = AttendanceManager(db)
#     manager.delete_lab_data(lab_no,system_no,student_id,date)
#     del manager

#     return redirect(request.META.get('HTTP_REFERER', '/'))


def get_key(key,val,finished):
    for value in finished:
        if val == value:
            return True
        else:
            False

# def add_theory_attendance(request,batch_id):
#     batch = BatchModel.objects.get(id=batch_id)
    
#     if 'date' in request.GET:
#         date = request.GET.get('date')
#     else:
#         if request.method == 'POST':
            
#             date = request.POST['date']
#             content =""
#             entry_time = ""
#             exit_time = ""
#             batch.initialize_batch_attendance(date,content,entry_time,exit_time)
#             return HttpResponseRedirect(request.path + f"?date={date}&entrytime={entry_time}&exittime={exit_time}")
#         else:
#             form = DateForm()
#         return render(request, 'theory_date_form.html', {'form': form})

    
#     if request.method == 'POST':
#         #content = request.POST.get('content')
#         content = request.POST.getlist('content')
#         entry_time = request.POST.get('entrytime')
#         exit_time = request.POST.get('exittime')
#         students_present = request.POST.getlist('students')
#         for student in batch.batch_students.all():
#             print(students_present)
#             status = "present" if str(student.enrol_no) in students_present else "absent"
#             batch.add_theory_attendance(content,entry_time,exit_time,student.enrol_no,status,date)
#         return redirect(request.META.get('HTTP_REFERER', '/'))
#     existing_data = batch.get_attendance_data(date)
#     """
#     #for the previous without day contents
#     contents_to_include = batch.batch_course.contents
#     contents_list = contents_to_include.splitlines()
#     removed = sorted(list(set(contents_list)-set(batch.finished_topics())))
#     """
#     contents = batch.batch_course.get_day_contents()
#     #print(contents)
#     finished_topics = batch.finished_topics()
#     removed = [key  for key, value in contents.items() if get_key(key,value,finished_topics)  ]
#     print(removed)
#     return render(request,"theory_attendance_form.html",{"data":existing_data,"batch":batch,"contents":removed,"org_contents":contents})


# def delete_theory_attendance(request,**kwargs):
#     batch_id = kwargs.get("batch_id","")
#     date = kwargs.get("date","")
#     student_id = kwargs.get("stud_id")
#     manager = AttendanceManager(db)
#     manager.delete_attendance(batch_id=batch_id,date=date,student_id=student_id)
#     return redirect(request.META.get('HTTP_REFERER', '/'))


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
            'enroll':student.enrol_no,
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


# def lab_dashboard(request,lab_id):
#     date = request.GET.get("date")
#     if date == None:
#         date = datetime.today()
        
#     lab = LabSystemModel.objects.get(id=lab_id)
#     systems = lab.get_systems()
#     data = lab.get_attendance_data(date)
#     time_slots = [f'{h:02d}:{m:02d}' for h in range(0, 24) for m in (0, 30)]

#     students = Student.objects.filter(current_status="active")
#     students_id = [{"id": student.enrol_no, "name": student.student_name} for student in students]
#     context = {
#         "system_data_dict": data, 
#         "students": students_id, 
#         "systems": systems,
#         "lab_no":lab_id,
#         "date":date,
#         'time_slots': time_slots,
#     }
#     student_id = request.GET.get('student_id')
#     week = request.GET.get('week')
#     if student_id != None and week != None:
#         student = Student.objects.get(enrol_no=student_id)
#         manager = AttendanceManager(db)
#         context["student_data"] = manager.get_student_lab_data(str(student.enrol_no),week)
#         return render(request,"lab_dashboard.html",context) 
        
        
#     return render(request,"lab_dashboard.html",context) 

# def theory_dashboard(request):
#     staff_id = request.GET.get("staff_id")
#     staffs = Staff.objects.all()
#     staff_list = [{"id":s.id,"name":s.username} for s in staffs]
#     if not staff_id:
#         return render(request,'theory_dashboard_form.html',{'staff_list':staff_list})
#     batch_id = request.GET.get("batch")
#     date = request.GET.get("date")
#     staff = Staff.objects.get(id=int(staff_id))
    
#     staff_list = [{"id":s.id,"name":s.username} for s in staffs]
#     batches = BatchModel.objects.filter(batch_staff = staff)
#     manager = AttendanceManager(db)
#     result = {}
#     for batch in batches:
#         data = manager.get_theory_dashboard(batch.id)
#         result[batch.get_batch_name()] = data
    
        
#     all_batches = BatchModel.objects.all()
#     batch_list = [{"id":b.id,'name':b.get_batch_name()} for b in batches]
#     context = {
#         "data_for_staff":result,
#         "staff_list":staff_list,
#         "batch_list":batch_list,
#     }
#     #print(context)
#     if batch_id and date:
        
#         doc = manager.get_theory_data(int(batch_id),date)
#         if doc :
#             doc.pop('_id', None)
#             students = doc.get('students', {})
#             mapped_students = {student_id: {'name': map_name(student_id), 'status': status} for student_id, status in students.items()}
#             doc['students'] = mapped_students

#             context['specific_date'] = doc
        
#     return render(request,"theory_dashboard.html",context)
    

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



#------------------------------------------------------------------------------------#
    
@csrf_exempt
def pre_batch_details(request,batch_id):
    batch = BatchModel.objects.get(id=batch_id)
    manager = AttendanceManagerV2(db)
    org_contents = list(batch.batch_course.get_day_contents().values()) #change it to get the un finished topics
    finished = [item for sublist in manager.get_finished_topics(batch_id) for item in sublist] 
    contents = []
    for content in org_contents:
        if content not in finished:
            contents.append(content)
    existing = None
    body = json.loads(request.body)
    
    req_contents = ast.literal_eval(body.get('prev_content',[]) if type(body)==dict else '[]')
    
    print('req_contents',req_contents,type(req_contents))
    if req_contents != []:
        existing = manager.get_theory_data(batch_id,req_contents)
        #debug_info(existing)
    
    students = batch.list_students(map_name=True)
    
    data = {
        "contents":org_contents,
        "batch_id":batch_id,
        "students":students,
        "existing":existing
    }   
    #debug_info(data)

    return JsonResponse(data)

def show_form(request,batch_id):
    batch = BatchModel.objects.get(id=batch_id)
    staffs = Staff.objects.all()
    staffs = [{'id':staff.id,'name':staff.name} for staff in staffs]
    data = {
        "batch_id":batch_id,
        "staffs":staffs,
        "batch_staff":batch.batch_staff
    }
    #debug_info(data)
    return render(request,'v2/theory_form.html', data)


@csrf_exempt
def save_theory_attendance(request,batch_id):
    body = json.loads(request.body)
    debug_info(body)
    # return JsonResponse({'message':'success'})
    manager = AttendanceManagerV2(db)
    result = manager.add_data(batch_id,body)
    #debug_info(result)
    return JsonResponse({'message':result})


def get_theory_attendance(request,batch_id):
    manager = AttendanceManagerV2(db)
    batch = BatchModel.objects.get(id=batch_id)
    finished_topics = manager.get_finished_topics(batch_id)
    contents = list(batch.batch_course.get_day_contents().values())
    #debug_info(finished_topics)
    data = {
        'finsihed':finished_topics,
        'contents':contents
    }

    return JsonResponse(data)

#------lab attendance api-------------------#

def show_lab_form(request):
    students = Student.objects.filter(current_status="active")
    students_id = [{"number": str(student.enrol_no), "name": student.student_name} for student in students]
    systems  = LabSystemModel.objects.all().first().get_systems()
    staffs = [{"name":staff.name,"id":staff.id} for staff in Staff.objects.all()]
    labs = list(LabSystemModel.objects.values('id','lab_no'))
    data = {
        "labs":labs,
        "students":students_id,
        "systems":systems,
        "staffs":staffs,
    }
    ##debug_info(data)
    return render(request,"lab_attendance_form.html",data)

def get_systems(request,lab_id):
    systems  = LabSystemModel.objects.get(id=lab_id).get_systems()
    return JsonResponse({"systems":systems})

def get_lab_attendance(request,lab_id,date):
    manager = AttendanceManagerV2(db)
    data = list(manager.get_lab_data(lab_id,date))
    # debug_info(data)
    maped_students = {}
    if len(data)>0:
        for students in data[0].values():
            for student in students:
                maped_students[student] = Student.objects.get(enrol_no=student).student_name
    else:
        data.append({});
    data.append({"students":maped_students})
    # debug_info(data)
    return JsonResponse(data,safe=False)

@csrf_exempt
def add_lab_data(request,lab_id,date):
    body = json.loads(request.body)
    sys = body.get('system_no')
    data = body.get('data')
    debug_info(body)
    stud = Student.objects.filter(enrol_no=data['student_id'])
    manager = AttendanceManagerV2(db)
    if not stud.exists():
        return JsonResponse({'message':"please provide correct student enrollment number","result":False})
    result,err = manager.put_lab_data(lab_id,date,sys,data['time'],data['student_id'],data['staff_id'])
    
    return JsonResponse({'message':result,"result":err,"name":stud[0].student_name})

@csrf_exempt
def delete_lab_data(request,lab_id,date):
    body = json.loads(request.body)
    sys,student_id,time = body.get('system_no'),body.get('student_id'),body.get('time')
    manager = AttendanceManagerV2(db)
    result = manager.delete_lab_data(lab_id,date,sys,time,student_id)
    #debug_info(body)
    return JsonResponse({'message':result})

def get_lab_sys_data(request,lab_id,date,sys_no,start,end):
    manager = AttendanceManagerV2(db)
    debug_info((lab_id,date,sys_no,start,end))
    data = map(int,manager.get_lab_system_data(lab_id,date,sys_no,start,end))
    students = Student.objects.filter(enrol_no__in=data)
    students_id = [{"number": str(student.enrol_no), "name": student.student_name} for student in students]
    data = {
        'data':students_id,
    }
    return JsonResponse(data)


#------------------- analytics views ------------------

def show_theory_dashboard(request):
    manager = AnalyticManager()
    theory_shedule = manager.theory_sheet_data()
    students = [{"name":student.student_name,"id":str(student.enrol_no)} for student in Student.objects.filter(current_status="active")]
    staffs = [{"name":staff.name,"id":staff.id} for staff in Staff.objects.filter(current_status="active")]
    data = {
        "data":theory_shedule,
        "students":students,
        "staffs":staffs
    }
    return render(request,'v2/theory_dashboard.html',data)


#helper function to parse date from request
def parse_date(from_date,to_date):
    from_date = list(map(int,from_date.split('-')))
    end_date  = list(map(int,to_date.split('-')))
    debug_info(from_date)
    debug_info(end_date)
    start_date = date(from_date[0],from_date[1],from_date[2])  # Example start date
    end_date = date(end_date[0],end_date[1],end_date[2])  # Example start date
    
    return start_date,end_date

def staff_dashboard_data(request,staff_id,from_date,to_date):
    staff = Staff.objects.get(id=staff_id)
    manager = AnalyticManager()
    start,stop = parse_date(from_date,to_date)
    raw_data = manager.get_staff_data(staff,start,stop)
    
    return JsonResponse(raw_data,safe=False)


def lab_dashboard(request,lab_id):
    return HttpResponse("Not Implemented yet")
