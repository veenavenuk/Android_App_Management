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


# Login  
class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:   
            serializer = UserLoginSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)

                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                dashboard_url = self.get_dashboard_url(user)

                return Response({
                    "message": "Login successful!",
                    "dashboard_url": dashboard_url,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "token": token.key
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Error: ", e)
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)

    def get_dashboard_url(self, user):
        if user.groups.filter(name='admin').exists():
            return '/add-points'
        return '/user-view'
    

# Logout 
class Logout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


# Signup - User 
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


# Add new App - Admin 
class addAppSave(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

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


# View all app details - Admin 
class AppListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            apps = AndroidApp.objects.all()
            serializer = AppListSerializer(apps, many=True)
            return Response({"data" : serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Oops! Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)


# Add points to submitted task - Admin 
class AddPointsView(View):
    def get(self, request):
        try:
            user = verify_token_from_cookie(request)
            if not user:
                return redirect('/')
            
            tsk_dtls = TaskManager.objects.all().order_by('status_id','android_app__app_name')            
            serializer = TaskManagerViewSerializer(tsk_dtls, many=True, context={'request': request})
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


# User Dashboard View 
class UserDashboardView(View):

    def get(self, request):
        try:
            user = verify_token_from_cookie(request)
            if not user:
                return redirect('/')

            serializer = userTaskMapperSerializer(user, many=False)
            return render(request, "user_dashboard.html", {"data": serializer.data})

        except Exception as e:
            return render(request, "error_page.html", {"message": "An error occurred."})


# Submit task - User 
class TaskSubmit(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            usr = request.user
            app_id = request.data.get('app_id') 
            screenshot = request.FILES.get('screenshot')

            android_app = AndroidApp.objects.get(id=app_id)
            status_data = Status.objects.filter(code="TSK_SBMTD").first()
        
            tskMngr=TaskManager(user=usr, android_app=android_app, status=status_data, created_by=usr, points=0, is_active=True, screenshot=screenshot)
            tskMngr.save()
            
            return Response({"message": "Sucessfully Added"}, status=status.HTTP_200_OK)
    
        except Exception as e:
            print("error : ",e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Verify - token 
def verify_token_from_cookie(request):
    '''
    Retrieves and validates the token from cookies.
    Returns the authenticated user if valid, otherwise None.'''
    
    token = request.COOKIES.get('auth_token')
    if not token:
        return None

    decoded_token = unquote(token)
    user_token = Token.objects.filter(key=decoded_token).first()

    return user_token.user if user_token else None


# View Login Page
class home(TemplateView):
    template_name = "login.html"


# Add App page - Admin 
class addApp(TemplateView):
    template_name = "admin_add_app.html"


# View submitted task
class taskDtls(TemplateView):
    template_name = "admin_task_dtls_view.html"

 

# Admin - Signup       
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





        
 

 


