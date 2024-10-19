from django.db import models
from .manager import AttendanceManager
from datetime import datetime
from csc_app.settings import db

class LabSystemModel(models.Model):
    lab_no = models.CharField(max_length=200,blank=True, null=True)
    systems = models.JSONField(default=list)\

    def get_systems(self):
        doc = self.systems
        systems = []
        for i in doc:
            systems.append(i["no"])

        return systems

    def append_system(self, system_name):
        systems = self.systems

        if not any(system['no'] == system_name for system in systems):
            systems.append({"no": system_name})
            self.systems = systems
            self.save()

    def delete_system(self, system_name):
        systems = self.systems
        systems = [system for system in systems if system["no"] != system_name]
        self.systems = systems
        self.save()

    def get_attendance_data(self,date):
        manager = AttendanceManager(db)
        result = {}
        for system in self.get_systems():
            result[system] = manager.get_lab_data(self.id,system,date)
            #print(result[system])
            if result[system] != None:
                result[system].pop("_id",'')
            if result[system] == None:
                result[system] = {'date': date, 'lab_no': self.id, 'system_no': system, 'data': {'not available': {'start': '00:00', 'stop': '01:00'}}}
            
        return result

    