import pymongo
from apps.staffs.models import Staff
from apps.students.models import Student
from apps.batch.models import BatchModel
from datetime import datetime
from csc_app.settings import mongo_uri


class DashboardManager:
    def __init__(self, mongodb_database):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongodb_database]
        self.staff_collection = self.db["staff_collection"]
        self.student_collection = self.db["student_collection"]
        self.theory_collection = self.db['theory_collection']

    def __del__(self):
        self.client.close()

    def get_staff_attendance(self, week_dates):
        staff_strength = Staff.objects.count()
        presentees = []

        for date in week_dates:
            staff_attendance = self.staff_collection.find_one({
                'date': date,
                'attendance': {'$exists': True, '$ne': {}}
            })
            #print(staff_attendance)
            if staff_attendance:
                present_staff = {k: v for k, v in staff_attendance.get('attendance', {}).items() if v.get('entry_time') and v.get('exit_time')}
                attendance_count = len(present_staff)
                presentees.append((date, attendance_count))
            else:
                presentees.append((date, 0))

        return staff_strength, presentees


    def get_student_attendance(self, week_dates):
        student_strength = Student.objects.count()
        presentees = []

        for date in week_dates:
            student_attendance = self.student_collection.find_one({
                'date': date,
                'attendance': {'$exists': True, '$ne': {}}
            })
            if student_attendance:
                present_students = {k: v for k, v in student_attendance.get('attendance', {}).items() if v.get('entry_time') and v.get('exit_time')}
                attendance_count = len(present_students)
                presentees.append((date, attendance_count))
            else:
                presentees.append((date, 0))

        return student_strength, presentees


    def get_student_table(self, date):
        document = self.student_collection.find_one({"date": date})
        if document:
            data = document.get("attendance", {})

            students_data = []
            for student_id, attendance_data in data.items():
                student = Student.objects.filter(id=int(student_id)).first()
                if student:
                    students_data.append({
                        'student_id': student.enrol_no,
                        'name': student.student_name,
                        'entry_time': attendance_data.get("entry_time", ""),
                        'exit_time': attendance_data.get("exit_time", "")
                    })

            return students_data
        else:
            return []

    def get_staff_table(self, date):
        document = self.staff_collection.find_one({'date': date})
        if document:
            data = document.get('attendance', {})

            staffs_data = []
            for staff_id, attendance_data in data.items():
                staff = Staff.objects.get(id=int(staff_id))
                if staff:
                    staffs_data.append({
                        'staff_id': staff.id,
                        'name': staff.username,
                        'entry_time': attendance_data.get("entry_time", ""),
                        'exit_time': attendance_data.get("exit_time", "")
                    })

            return staffs_data
        else:
            return []
        
        
    def get_public_attendance(self,student_id,batch_id):
        
        docs = self.theory_collection.find({"batch_id":batch_id})
        #print(docs)
        result = []
        for doc in docs:
            #print(doc)
            result.append(format_document(student_id,doc))
        
        return result

def format_document(student_id,doc):
    formatted_doc = {
        'date': doc['date'],
        'content': doc['content'],
        'time_string': f"{doc['entry_time']} - {doc['exit_time']}",
        'student_status': doc['students'].get(str(student_id), 'not found')
    }
    return formatted_doc