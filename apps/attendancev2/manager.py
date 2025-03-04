import pymongo
import datetime
from csc_app.settings import mongo_uri,db
from apps.corecode.utils import debug_info
from apps.staffs.models import Staff
class AttendanceManager:
    def __init__(self,mongodb_database):
        self.db_name = mongodb_database
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[self.db_name]
        self.staff_collection = self.db['staff_collection']
        self.student_collection = self.db['student_collection']
        self.lab_collection = self.db['lab_collection']
        self.theory_collection = self.db['theory_collection']

    def put_lab_collection(self,lab_no,system_no,student_id,start,stop,date):
        doc = self.lab_collection.find_one({"date":date,"system_no":system_no,"lab_no":lab_no})

        if not doc:
            doc = {
                "date":date,
                "lab_no":lab_no,
                "system_no":system_no,
                "data":{
                    student_id:{
                        "start":start,
                        "stop":stop
                    }
                }
            }
        
            self.lab_collection.insert_one(doc)

        else:
            
            usage_data = {
                "start":start,
                "stop":stop
            }

            self.lab_collection.update_one(
            {"date": date,"lab_no":lab_no,"system_no":system_no},
            {"$set": {f"data.{student_id}": usage_data}})

            print("came here")


    def delete_lab_data(self, lab_no, system_no, student_id, date):
        query = {"date": date, "lab_no": lab_no, "system_no": system_no}
        update_query = {"$unset": {f"data.{student_id}": ""}}
        
        print("Query:", query)
        print("Update Query:", update_query)

        try:
            result = self.lab_collection.update_one(query, update_query)
            if result.modified_count > 0:
                print("Data deleted successfully")
            else:
                print("No matching documents found for deletion")
        except Exception as e:
            print("An error occurred:", e)


    def get_lab_data(self,lab_no,system_no,date):
        
        doc = self.lab_collection.find_one({"date":date,"lab_no":lab_no,'system_no':system_no})
    
        return doc


    def initialize_batch(self, batch_id, date,content,entry_time,exit_time,students):
        # Check if batch already exists for the given batch_id and date
        existing_batch = self.theory_collection.find_one({"batch_id": batch_id, "date": date})

        if existing_batch is None:
            document = {
                "batch_id": batch_id,
                "date": date,
                "content":content,
                "entry_time":entry_time,
                "exit_time":exit_time,
                "students": students
            }
            self.theory_collection.insert_one(document)

    def add_theory_attendance(self, batch_id, student_id, date, status, content, entry_time, exit_time):
        result = self.theory_collection.update_one(
            {"batch_id": batch_id, "date": date},
            {
                "$set": {
                    f"students.{student_id}": status,
                    "content": content,
                    "entry_time": entry_time,
                    "exit_time": exit_time
                }
            }
        )
        if result.modified_count > 0:
                print("modified")
        else:
            print("No matching documents found for for modification")

    def delete_attendance(self, batch_id, student_id, date):
        self.theory_collection.update_one(
            {"batch_id": batch_id, "date": date},
            {"$unset": {f"students.{student_id}": ""}}
        )

    def get_theory_data(self,batch,date):
        doc = self.theory_collection.find_one({"batch_id":batch,"date":date})
        
        
    def get_theory_data_v2(self,batch,contents):
        print({"batch_id":batch,"content":{"$elemMatch":{"$eq":contents}}})
        doc = self.theory_collection.find_one({"batch_id":batch,"content":{"$elemMatch":{"$in":contents}}})
        # debug_info(doc)
        return doc


    def get_student_lab_data(self, student_id, week=None):
        if week is None:
            # Default to the current week
            today = datetime.datetime.now()
            year, week_number = today.strftime("%Y-%W").split("-")
        else:
            year, week_number = week.split("-W")
            year = int(year)
            week_number = int(week_number)

        # Calculate the start and end dates of the week
        start_of_week = datetime.datetime.strptime(f"{year}-{week_number}-1", "%Y-%W-%w")
        end_of_week = start_of_week + datetime.timedelta(days=6)

        week_query = {
            "date": {
                "$gte": start_of_week.strftime("%Y-%m-%d"),
                "$lte": end_of_week.strftime("%Y-%m-%d")
            }
        }

        # Define the pipeline
        pipeline = [
            {"$match": {"data." + str(student_id): {"$exists": True}}},
            {"$match": week_query}
        ]

        # Aggregate using pipeline
        week_documents = list(self.lab_collection.aggregate(pipeline))

        formatted_data = []
        for doc in week_documents:
            formatted_doc = {
                "date": doc["date"],
                "lab_no": doc["lab_no"],
                "system_no": doc["system_no"],
                "start_time": doc["data"][str(student_id)]["start"],
                "end_time": doc["data"][str(student_id)]["stop"]
            }
            formatted_data.append(formatted_doc)

        return formatted_data
    
    def get_theory_dashboard(self,batch_id):
        # Fetch documents from MongoDB
        documents = self.theory_collection.find({"batch_id": batch_id})
        #print(documents)
        # Initialize dictionary to store data
        batch_data = {}

        # Process fetched documents
        for doc in documents:
            date = doc["date"]
            content = doc['content']
            total_count = len(doc["students"])
            total_present = list(doc["students"].values()).count("present")
            total_absent = total_count - total_present

            # Update batch data for the current date
            if date in batch_data:
                batch_data[date]["total_count"] += total_count
                batch_data[date]["total_present"] += total_present
                batch_data[date]["total_absent"] += total_absent
            else:
                batch_data[date] = {
                    "batch_id":batch_id,
                    "content":content,
                    "total_count": total_count,
                    "total_present": total_present,
                    "total_absent": total_absent
                }
        #print(batch_data)
        return batch_data
    
    """here the student id is students enroll number it suits for all documents wedont use model id in documents"""
    def get_public_student_lab_data(self, student_id):


        # Define the pipeline
        pipeline = [
            {"$match": {"data." + str(student_id): {"$exists": True}}},
            {"$sort":{"date":1}}
        ]

        # Aggregate using pipeline
        week_documents = list(self.lab_collection.aggregate(pipeline))
        formatted_data = []
        for doc in week_documents:
            formatted_doc = {
                "date": doc["date"],
                "lab_no": doc["lab_no"],
                "system_no": doc["system_no"],
                "start_time": doc["data"][str(student_id)]["start"],
                "end_time": doc["data"][str(student_id)]["stop"]
            }
            formatted_data.append(formatted_doc)
        #print(formatted_data)
        return formatted_data
    
    def get_all_theory_data(self,batch_id):
        documents = self.theory_collection.find({"batch_id": batch_id})
        #print(documents)
        return documents
        
class AttendanceManagerV2:
    def __init__(self,mongodb_database):
        self.db_name = mongodb_database
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[self.db_name]
        self.staff_collection = self.db['staff_collection']
        self.student_collection = self.db['student_collection']
        self.lab_collection = self.db['lab_collection']
        self.theory_collection = self.db['theory_collection']
        
    #------------------theory----------------
    
    def get_batch_data(self,batch_id):
        data = self.theory_collection.find({"batch_id":batch_id})
        result = []
        for doc in data:
            doc.pop('_id','batch_id')
            result.append(doc)
            
        return result
    
    def get_theory_data(self,batch,contents):
        doc = self.theory_collection.find_one({"batch_id":batch,"content":{"$elemMatch":{"$in":contents}}})
        # debug_info(doc)
        doc.pop('_id')
        return doc


    def add_data(self,batch_id,data):
        debug_info({'batch_id':batch_id,'content':{"$in":data['contents']}})
        doc = self.theory_collection.find_one({'batch_id':batch_id,'content':{"$in":data['contents']}})
        
        if doc:
            self.theory_collection.update_one(
                {'batch_id':batch_id,'content':{"$in":data['contents']}},
                {'$set':{'sessions':data['sessions'],'content':data['contents']}}
            )
            return 'data updated'
        else:
            self.theory_collection.insert_one(
                {'batch_id':batch_id,
                 'content':data['contents'],
                 'sessions':data['sessions']
                }
            )
            
            return 'data inserted'
        
    def get_finished_topics(self,batch_id,with_date=False):
        docs = self.theory_collection.find({'batch_id':batch_id})
        if not with_date:
            result = []
            for doc in docs:
                result.append(doc['content'])
            
            return result
        else:
            result = {}
            for doc in docs:
                print(doc)
                result[doc['sessions'][0]['date']] = doc['content']
                
            return result
    
    def get_finished_topics_batch(self,batch_id):
        docs = self.theory_collection.find({'batch_id':batch_id})
        result1 = []
        result2 = []
        for doc in docs:
            # debug_info(doc)
            result1.append(doc['content'])
            result2.append({"content":doc['content'],"staff":Staff.objects.get(id=doc['sessions'][0]['staff']),'date':doc['sessions'][0]['date']})
        return result1,result2
        
    #----------lab---------------
    def get_lab_data(self,lab_no,date):
        # debug_info({"date":str(date),"lab_id":lab_no})
        # docs = self.lab_collection.find({"date":str(date),"lab_id":lab_no})
        # res = []
        # for doc in docs:
        #     doc.pop('_id')
        #     res.append(doc)
        # return res
        pipeline = [
            {"$match": {"lab_id": lab_no, "date": date}},
            {"$unwind": "$data"},
            {
                "$project": {
                    "key": {"$concat": ["$system_no", "_", {"$substr": ["$data.start", 0, 2]}]},
                    "students": "$data.students",
                }
            },
            {"$group": {"_id": "null", "result": {"$push": {"k": "$key", "v": "$students"}}}},
            {"$replaceRoot": {"newRoot": {"$arrayToObject": "$result"}}},
        ]
        
        doc = self.lab_collection.aggregate(pipeline)
        # debug_info(doc)
        return doc
    
    def roughwork(self,num,data):
        doc = self.theory_collection.find_one({"num":num})
        result = doc
        if not doc:
            self.theory_collection.insert_one({"num":num})
        else:
            result = self.theory_collection.update_one({"num":num},{"$set":{"data":data}})
        return result
        
    # def put_lab_data(self,lab_no,date,data):
    #     doc = self.lab_collection.find_one({"date":date,"lab_no":lab_no,"system_no":data['system_no']})
    #     if doc:
    #         self.lab_collection.update_one(
    #             {"date": date,"lab_no":lab_no,"system_no":data['system_no']},
    #             {"$set": {f"data.{data['student_id']}": {
    #                     "start":data['start'],
    #                     "stop":data['stop']
    #                     }
    #                 }
    #              }
    #         )
    #         return 'data updated'
    #     else:
    #         doc = {
    #             "date":date,
    #             "lab_no":lab_no,
    #             "system_no":data['system_no'],
    #             "data":{
    #                 data['student_id']:{
    #                     "start":data['start'],
    #                     "stop":data['stop']
    #                 }
    #             }
    #         }
    #         self.lab_collection.insert_one(doc)
    #         return 'data inserted'
        
    def put_lab_data(self, lab_no, date, sys, time, student, staff):
        doc = self.lab_collection.find_one({"lab_id": lab_no, "system_no": sys, "date": date})
        
        if not doc:
            # Create a new document
            doc = {
                "lab_id": lab_no,
                "system_no": sys,
                "date": date,
                "data": [
                    {
                        "start": time['start'],
                        "end": time['end'],
                        "students": [student],
                        "incharges": [staff]
                    }
                ]
            }
            self.db.lab_collection.insert_one(doc)
            return "data inserted",True
        else:
            for ele in doc['data']:
               if ele['start'] == time['start'] and ele['end'] == time['end'] and len(ele['students']) >= 2:
                    return "Maximum Student Limit Reached for the system",False
            
            result = self.db.lab_collection.update_one(
                {
                    "lab_id": lab_no,
                    "system_no": sys,
                    "date": date,
                    "data": {
                        "$elemMatch": {
                            "start": time['start'],
                            "end": time['end']
                        }
                    }
                },
                {
                    "$addToSet": {
                        "data.$.students": student,  
                        "data.$.incharges": staff
                    }
                }
            )
            
            if result.modified_count > 0:
                return "data updated",True
            
            new_time_slot = {
                "start": time['start'],
                "end": time['end'],
                "students": [student],
                "incharges": [staff]
            }
            result = self.db.lab_collection.update_one(
                {
                    "lab_id": lab_no,
                    "system_no": sys,
                    "date": date
                },
                {
                    "$push": {
                        "data": new_time_slot
                    }
                }
            )
            
            if result.modified_count > 0:
                return "new time slot added",True
        
        return "no changes made",True

  
    def get_lab_staff(self, lab_no, date, sys, time):
        # Query to find the lab document with the matching time slot
        doc = self.lab_collection.find_one(
            {
                "lab_id": lab_no,
                "system_no": sys,
                "date": date,
                "data": {
                    "$elemMatch": {
                        "start": time['start'],
                        "end": time['end']
                    }
                }
            }
        )
        
        if doc:
            # Extract the staff list for the matching time slot
            for time_slot in doc['data']:
                if time_slot['start'] == time['start'] and time_slot['end'] == time['end']:
                    return time_slot['incharges']  # Return the list of staff (incharges)
        
        return "No staff found for the given time slot."

    def get_lab_system_data(self,lab_no,date,sys,start,end):
        data = self.lab_collection.find_one({"lab_id": lab_no,"system_no":sys,"date": date})
        debug_info({"lab_id": lab_no,"system_no":sys,"date": date})
        debug_info(data)
        if data:
            for doc in data['data']:
                if doc['start'] == start and doc['end'] == end:
                    return doc['students']
            else:
                return []
        else:
            return []
        
    def delete_lab_data(self,lab_no,date,sys,time,student):
        result = self.db.lab_collection.update_one({"lab_id": lab_no,"system_no":sys,"date": date,'data.start': time['start'],'data.end':time['end']},
                        {
                            "$pull": {
                                'data.$.students': student
                            }
                        }
                    );
    
class DailyAttendanceManager:
    def __init__(self, mongodb_database):
        self.db_name = mongodb_database
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[self.db_name]
        self.staff_collection = self.db["staff_collection"]
        self.student_collection = self.db["student_collection"]

    def initialize_staff(self, date):
        existing_staff = self.staff_collection.find_one({"date": date})
        if existing_staff is None:
            document = {
                "date": date,
                "attendance": {}
            }
            self.staff_collection.insert_one(document)

    def add_staff_attendance(self, staff_id ,date, entry_time, exit_time,status):
        attendance_data = {
            "entry_time": entry_time,
            "exit_time": exit_time,
            "status":status
        }
        self.staff_collection.update_one(
            {"date": date},
            {"$set": {f"attendance.{staff_id}": attendance_data}}
        )

    def update_staff_attendance(self, date, entry_time, exit_time):
        attendance_data = {
            "entry_time": entry_time,
            "exit_time": exit_time
        }
        self.staff_collection.update_one(
            {"date": date},
            {"$set": {"attendance": attendance_data}}
        )

    def get_staff_attendance(self, date):
        document = self.staff_collection.find_one({"date": date})
        if document:
            return document.get("attendance", {})
        return {}

    def delete_staff_attendance(self, date,entry_number):
        self.staff_collection.update_one(
            {"date": date},
            {"$set": {f"attendance.{entry_number}": {"status":"absent","entry_time":None,"exit_time":None}}}
        )

    def initialize_student(self, date):
        existing_student = self.student_collection.find_one({"date": date})
        if existing_student is None:
            document = {
                "date": date,
                "attendance": {}
            }
            self.student_collection.insert_one(document)

    def add_student_attendance(self, student_id,date, entry_time, exit_time,status):
        attendance_data = {
            "entry_time": entry_time,
            "exit_time": exit_time,
            "status":status
        }
        self.student_collection.update_one(
            {"date": date},
            {"$set": {f"attendance.{student_id}": attendance_data}}
        )

    def update_student_attendance(self, date, entry_time, exit_time):
        attendance_data = {
            "entry_time": entry_time,
            "exit_time": exit_time
        }
        self.student_collection.update_one(
            {"date": date},
            {"$set": {"attendance": attendance_data}}
        )

    def get_student_attendance(self, date):
        document = self.student_collection.find_one({"date": date})
        if document:
            return document.get("attendance", {})
        return {}

    def delete_student_attendance(self, date, entry_number):
        print(date,entry_number)
        self.student_collection.update_one(
            {"date": date},
            {"$set": {f"attendance.{entry_number}": {"status":"absent","entry_time":None,"exit_time":None}}}
        )


    def get_single_staff_details(self, staff_id, month, year):
        query = {
            'date': {
                '$gte': datetime.datetime(year, month, 1).strftime('%Y-%m-%d'),
                '$lt': datetime.datetime(year, month + 1, 1).strftime('%Y-%m-%d') if month < 12 else datetime.datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
            }
        }
        print(query)
        documents = self.staff_collection.find(query)

        staff_details = []
        for document in documents:
            print(document,"from manager")
            attendance_data = document.get('attendance', {}).get(str(staff_id), {})
            if attendance_data:
                try:
                    staff = Staff.objects.get(id=int(staff_id))
                    staff_details.append({
                        'staff_id': staff.id,
                        'name': staff.username,
                        'date': document.get('date'),
                        'entry_time': attendance_data.get("entry_time", ""),
                        'exit_time': attendance_data.get("exit_time", "")
                    })
                except Staff.DoesNotExist:
                    continue  

        return staff_details
    
    
    
        
             
        
        
        
            
        
    