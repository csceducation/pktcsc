from apps.batch.models import BatchModel
from apps.staffs.models import Staff
from apps.corecode.models import Time
from apps.corecode.utils import debug_info
from .manager import AttendanceManagerV2
from csc_app.settings import db

class AnalyticManager(AttendanceManagerV2):
    def __init__(self):
        super().__init__(db)
        
    def student_batch(self,student):
        batches = BatchModel.objects.all(students__contains=student.id)
        batch_ids = [batch.id for batch in batches]
        
        return batch_ids
    
    def theory_sheet_data(self):
        staffs = Staff.objects.filter(current_status = 'active')
        data = [] 
        for staff in staffs:
            staff_data = []
            batches = BatchModel.objects.filter(batch_staff=staff)
            for batch in batches:
                finished_topics = self.get_finished_topics(batch.id, with_date=True)
                contents = list(batch.batch_course.get_day_contents().values())
                # debug_info(finished_topics)
                # debug_info(contents)
                # topics = list(filter(lambda n: n not  in {item for sublist in finished_topics.values() for item in sublist}, contents))
                # print("next topics",topics)
                # next_topics = topics[0]

                staff_data.append(
                    {
                        "staff":f"{staff.id} - {staff.name}",
                        "start":batch.batch_timing.time.split("-")[0],
                        "end":batch.batch_timing.time.split("-")[1],
                        "strength":batch.batch_students.count(),
                        "course":batch.batch_course.name,
                        "topics":{
                            "finished":finished_topics,
                            # "next":next_topics,
                            "contents":contents
                        }
                    }
                )
            data.append(staff_data)
        debug_info(data)
        return data
        
        
    def get_staff_data(self,staff,from_date,to_date):
        
        batches = BatchModel.objects.filter(batch_staff=staff,batch_start_date__gte=from_date,batch_end_date__lte=to_date)
        batch_data = {}
        batch_info = []
        total_classes = []
        completed_topics = []
        uncovered_topics = []
        for batch in batches:
            batch_data[batch.batch_id] = self.get_batch_data(batch.id)
            covered = []
            for data in batch_data[batch.batch_id]:
                covered.extend(data['content'])
            completed_topics.append({batch.batch_id:covered})
            uncovered_topics.append({batch.batch_id:list(filter(lambda x: x not in covered, batch.batch_course.get_contents()))})
            # total_classes.extend(batch.batch_course.get_contents())
            extra = {
                "students":batch.batch_students.count(),
                "subject":batch.batch_course.name,
                "student_data":[{"name":student.student_name,"enrol":student.enrol_no} for student in batch.batch_students.all()]
            }
            batch_info.append({batch.batch_id:extra})
        data= {
            "batch_data":batch_data,
            "batch_info":batch_info,
            "completed":completed_topics,
            "uncovered":uncovered_topics
        }
        # return data
        debug_info(data)
        
        return data
    
    def get_student_batch_data(self,stud_id):
        data = self.theory_collection.aggregate([
            { 
                "$unwind": "$sessions" 
            },
            {
                "$match": {
                "sessions.students": str(stud_id)
                }
            },
            {
                "$project": {
                "batch_id": 1,
                "date": "$sessions.date",
                "entry": "$sessions.entry",
                "exit": "$sessions.exit",
                "staff": "$sessions.staff",
                "content": 1
                }
            },
            {
                "$group": {
                "_id": "$batch_id",  #Grouping by batch_id
                "sessions": {
                    "$push": {
                    "date": "$date",
                    "entry": "$entry",
                    "exit": "$exit",
                    "staff": "$staff",
                    "content": "$content"
                    }
                }
                }
            },
            { 
                "$sort": { "_id": 1 }  # Sorting by batch_id
            }
        ])
        temp = []
        for doc in data:
            temp.append(doc)
        debug_info(temp)
        return temp
        
        
    #----------lab analysis--------------------#
    def get_lab_usage_time(self, lab_id, start_date, end_date):
        
        pipeline = [
            {"$match": {"lab_id": lab_id, "date": {"$gte": start_date, "$lte": end_date}}},
            {"$unwind": "$data"},
            {"$project": {
                "_id": 0,
                "lab_id": 1,
                "system_no": 1,
                "start": "$data.start",
                "end": "$data.end"
            }},
            {"$group": {
                "_id": {"lab_id": "$lab_id", "system_no": "$system_no"},
                "totalUsageMinutes": {
                    "$sum": {
                        "$subtract": [
                            {"$toDate": {"$concat": ["2024-12-28T", "$end", ":00"]}},
                            {"$toDate": {"$concat": ["2024-12-28T", "$start", ":00"]}}
                        ]
                    }
                }
            }},
            {"$project": {
                "_id": 0,
                "lab_id": "$_id.lab_id",
                "system_no": "$_id.system_no",
                "totalUsageHours": {"$divide": ["$totalUsageMinutes", 3600000]}  # Convert milliseconds to hours
            }}
        ]
        
        return list(self.lab_collection.aggregate(pipeline))
    
    
    def get_timings_by_staff(self, staff_id, start_date, end_date):
        
        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lte": end_date}}},
            {"$unwind": "$data"},
            {"$match": {"data.incharges": staff_id}},
            {"$project": {
                "_id": 0,
                "lab_id": 1,
                "system_no": 1,
                "date": 1,
                "start": "$data.start",
                "end": "$data.end"
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))



    def get_staff_and_students(client, lab_id, system_no, start_date, end_date):
        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lte": end_date}, "lab_id": lab_id, "system_no": system_no}},
            {"$unwind": "$data"},
            {"$group": {
                "_id": {
                    "lab_id": "$lab_id",
                    "system_no": "$system_no",
                    "date": "$date",
                    "start": "$data.start",
                    "end": "$data.end"
                },
                "incharges": {"$addToSet": "$data.incharges"},
                "students": {"$addToSet": "$data.students"}
            }},
            {"$project": {
                "_id": 0,
                "lab_id": "$_id.lab_id",
                "system_no": "$_id.system_no",
                "date": "$_id.date",
                "timeSlot": {"start": "$_id.start", "end": "$_id.end"},
                "incharges": {"$reduce": {"input": "$incharges", "initialValue": [], "in": {"$setUnion": ["$$value", "$$this"]}}},
                "students": {"$reduce": {"input": "$students", "initialValue": [], "in": {"$setUnion": ["$$value", "$$this"]}}}
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))



    def get_staff_incharge_report(self, start_date, end_date):
        
        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lte": end_date}}},
            {"$unwind": "$data"},
            {"$project": {
                "_id": 0,
                "date": 1,
                "lab_id": 1,
                "system_no": 1,
                "start": "$data.start",
                "end": "$data.end",
                "incharges": "$data.incharges"
            }},
            {"$unwind": "$incharges"},
            {"$group": {
                "_id": {
                    "date": "$date",
                    "lab_id": "$lab_id",
                    "system_no": "$system_no",
                    "timeSlot": {"start": "$start", "end": "$end"}
                },
                "staff": {"$addToSet": "$incharges"}
            }},
            {"$project": {
                "_id": 0,
                "date": "$_id.date",
                "lab_id": "$_id.lab_id",
                "system_no": "$_id.system_no",
                "timeSlot": "$_id.timeSlot",
                "staff": 1
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))

# # Example Usage
# staff_incharge_report = get_staff_incharge_report(client, start_date, end_date)
# print(staff_incharge_report)


# # Example Usage
# staff_and_students = get_staff_and_students(client, 1, "sys1", start_date, end_date)
# print(staff_and_students)



# # Example Usage
# staff_timings = get_timings_by_staff(client, 1, start_date, end_date)
# print(staff_timings)

    
    
        