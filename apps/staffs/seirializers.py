# from rest_framework import serializers
# from .models import Staff
# from apps.corecode.models import Subject


# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = ['id','name']

# class StaffSerializer(serializers.ModelSerializer):
#     known_subjects = SubjectSerializer(many=True)
#     class Meta:
#         model = Staff
#         fields = ['id','known_subjects','name']
        
#     def to_representation(self, instance):
#         # If instance is empty, return an empty list
#         if not instance:
#             return []
#         return super().to_representation(instance)