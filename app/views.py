from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers import *
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .models import *
from urllib.parse import unquote
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect


# @method_decorator(login_required(login_url='/'), name='dispatch')
class home(TemplateView):
    template_name = "login.html"

# @method_decorator(login_required(login_url='/'), name='dispatch')
class addApp(TemplateView):
    template_name = "admin_add_app.html"

# @method_decorator(login_required(login_url='/'), name='dispatch')
class taskDtls(TemplateView):
    template_name = "admin_task_dtls_view.html"
    
class Login(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:    
            serializer = UserLoginSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                groups = user.groups.values_list('name', flat=True) 
                if 'admin' in groups:
                    dashboard_url = '/add-points' 
                else:
                    dashboard_url = '/user-view' 
                
                return Response({
                    "message": "Login successful!",
                    "dashboard_url": dashboard_url,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "token": token.key,}, status=status.HTTP_200_OK)
                  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error: ", e)
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)

class Logout(View):
    def get(self, request):
        logout(request)  
        return redirect('home')
    
class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:  
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                try:
                    group = Group.objects.get(name="user")
                    user.groups.add(group)
                except Group.DoesNotExist:
                    return Response({"message": "Group does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)

class addAppSave(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            serializer = AddAppSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "App added successfully!"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
             
        except Exception as e:
            print("ERROR :",e)
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)

class AppListView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            apps = AndroidApp.objects.all()
            serializer = AppListSerializer(apps, many=True)
            return Response({"data" : serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator(login_required(login_url='/'), name='dispatch')
class UserDashboardView(View):
    def get(self, request):
        try:
            token = request.GET.get('token')
            if token:
                decoded_token = unquote(token)
                user_token = Token.objects.filter(key=decoded_token).first() 
                if user_token:
                    user_data = user_token.user 
                    serializer = userTaskMapperSerializer(user_data, many=False)
                    
                    return render(request, "user_dashboard.html", {"data": serializer.data})
 
        except Exception as e:
            print("Error: ", e)
            return render(request, "error_page.html", {"message": "An error occurred."})
        

@method_decorator(csrf_exempt, name='dispatch')
# @method_decorator(login_required(login_url='/'), name='dispatch')
class AddPointsView(View):
    def get(self, request):
        try:
            # token = request.GET.get('token')
            # if token:
            #     decoded_token = unquote(token)
            #     user_token = Token.objects.filter(key=decoded_token).first() 
            #     if user_token:
            tsk_dtls = TaskManager.objects.all().order_by('status_id','android_app__app_name')            
            serializer = TaskManagerViewSerializer(tsk_dtls, many=True)
            
            return render(request, "admin_add_points.html", {"data": serializer.data})
        
        except Exception as e:
            print("Error: ", e)
            return render(request, "error_page.html", {"message": "An error occurred."})
        
    def post(self, request):
        try:
            tsk_mngr_id = request.POST['task_id']
            points = request.POST['points'] 

            tsk_obj = TaskManager.objects.filter(id=tsk_mngr_id).first()
            status_obj=Status.objects.filter(code="TSK_CMPLTD").first()
            if tsk_obj:
                tsk_obj.points = points
                tsk_obj.status = status_obj
                tsk_obj.save()
            return self.get(request)

        except Exception as e:
            print("Error: ", e)
            return render(request, "error_page.html", {"message": "An error occurred."})
        
class TaskSubmit(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            usr = request.user
            app_id = request.data.get('app_id') 
            # screenshot = request.FILES.get('screenshot')

            android_app = AndroidApp.objects.get(id=app_id)
            status_data = Status.objects.filter(code="TSK_SBMTD").first()
        
            tskMngr=TaskManager(
                user=usr,
                android_app=android_app,
                status=status_data,
                created_by=usr,
                points=0,
                is_active=True
            )
            tskMngr.save()
            
            return Response({"message": "Sucessfully Added"}, status=status.HTTP_200_OK)
    
        except Exception as e:
            print("error : ",e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminSignup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:  
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()

                user.is_superuser = True
                user.is_staff = True
                user.save()
                
                try:
                    group = Group.objects.get(name="admin")
                    user.groups.add(group)
                except Group.DoesNotExist:
                    return Response({"message": "Group does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)
        
class CreateGroupsAPIView(APIView):
    def post(self, request):
        groups = ['admin', 'user']
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                print(f'Group "{group_name}" created.')
            else:
                print(f'Group "{group_name}" already exists.')
        
        return Response({'message': 'Groups checked/created successfully'}, status=status.HTTP_201_CREATED)
        


class AddStatusDataAPIView(APIView):
    def post(self, request):
        statuses = [
            {
                "name": "Pending",
                "code": "PND",
                "description": "Pending tasks"
            },
            {
                "name": "Submitted",
                "code": "TSK_SBMTD",
                "description": "Submitted Task"
            },
            {
                "name": "Task Completed",
                "code": "TSK_CMPLTD",
                "description": "Completed Task"
            }
        ]

        created = []
        skipped = []

        for status_data in statuses:

            TaskManager.objects.all().delete()

            user = User.objects.get(username="admin")
            user.set_password("Admin@1234") 
            user.save()

            obj, created_flag = Status.objects.get_or_create(
                code=status_data["code"],
                defaults={
                    "name": status_data["name"],
                    "description": status_data["description"]
                }
            )
            if created_flag:
                created.append(status_data["code"])
            else:
                skipped.append(status_data["code"])

        return Response({
            "created": created,
            "skipped_existing": skipped,
            "message": "Statuses processed successfully."
        }, status=status.HTTP_201_CREATED)





        
 

 


