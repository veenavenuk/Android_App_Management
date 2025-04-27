from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    contact_number = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'contact_number']

    def validate_email(self,data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError("Email is already registered.")
        return data

    def validate_username(self,data):
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError("Username already exists.")
        return data

    def validate_contact_number(self,data):
        if not data.isdigit():
            raise serializers.ValidationError("Mobile number must be numeric.")
        if len(data) < 8 or len(data) > 15:
            raise serializers.ValidationError("Mobile number must be between 8 and 15 digits.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data['username']
        password = data['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is not active.")
                
                data['user'] = user
                
            else:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Both username and password are required.")
        
        return data    


class AddAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = AndroidApp
        fields = ['app_name', 'package_name', 'app_version', 'category', 'contact_email', 'description']


class AppListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AndroidApp
        fields = '__all__'


class userTaskMapperSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    points_earned = serializers.SerializerMethodField()
    tasks_completed = serializers.SerializerMethodField()
    app_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','name','email','contact_number',"points_earned","tasks_completed","app_details"]

    def get_name (self,obj):
        return obj.first_name + " " + obj.last_name 
    
    def get_points_earned (self,obj):
        sum_points = sum([task.points if task.points is not None else 0 for task in TaskManager.objects.filter(user=obj)])
        return sum_points
    
    def get_tasks_completed (self,obj):
        TaskManager_obj=TaskManager.objects.filter(user=obj,status__code="TSK_CMPLTD").count()
        return TaskManager_obj
    
    def get_app_details (self,obj):
        apps = AndroidApp.objects.all().order_by('app_name') 
        tsk_dtl=userTaskDetailsSerializer(apps,many=True,context={'user_id': obj.id})
        return tsk_dtl.data


class userTaskDetailsSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = AndroidApp
        fields = ['id','app_name',"points","status"]
    
    def get_points (self,obj):
        user_id = self.context['user_id']
        usr=User.objects.filter(id=user_id).first()
        if(TaskManager.objects.filter(user=usr,android_app=obj).exists()==True):
            TaskManager_obj=TaskManager.objects.filter(user=usr,android_app=obj).first().points
        else:
            TaskManager_obj=0
        return TaskManager_obj
        
    def get_status (self,obj):
        user_id = self.context['user_id']
        usr=User.objects.filter(id=user_id).first()
        if(TaskManager.objects.filter(user=usr,android_app=obj).exists()==True):
            TaskManager_obj=TaskManager.objects.filter(user=usr,android_app=obj).first().status.name
        else:
            TaskManager_obj="Pending"
        return TaskManager_obj
 
    
class TaskManagerViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    android_app = serializers.CharField(source="android_app.app_name")
    status = serializers.CharField(source="status.name")
    screenshot = serializers.SerializerMethodField()

    class Meta:
        model = TaskManager
        fields = ['id','user', 'android_app', 'points', 'status', 'description','screenshot']

    def get_user (self,obj):
        return obj.user.first_name + " " + obj.user.last_name 
    
    def get_screenshot(self, obj):
        if obj.screenshot:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.screenshot.url)
        return None
    
    
  




     