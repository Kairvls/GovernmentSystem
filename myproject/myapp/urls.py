from django.urls import path

from . import views
from .views import viewdepartment
from .views import employee_dashboard

urlpatterns = [
    path('', views.checkin, name='checkin_page'),
    
    path('signup/', views.signup, name='signup'), 
    path('signin/', views.signin, name='signin'),
    path('employee-dashboard/', views.employee_dashboard, name='employee-dashboard'),
    
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('login/', views.login_view, name='login'),  
    path('departments/', views.departments, name='departments'),
    
  
    
    path('employeelist/', views.employeelist, name='employeelist'),
    
    path('departments/view/<int:department_id>/', viewdepartment, name='viewdepartment'),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('employee/<str:employee_id>/', views.view_employee, name='view_employee'),
    
     
     
     
    
]
