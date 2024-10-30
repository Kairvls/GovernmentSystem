from django.http import HttpResponse
from django.shortcuts import render, redirect    
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Department,Employee, Attendance
from django.utils import timezone
import pytz
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password

# User = get_user_model()
# user = User.objects.get(username='admin')  # Replace with your username
# print(user.password)  # This will show a hash, confirming the user exists.

def signin(request):
    return render(request, 'signin.html')

def signup(request):
    if request.method == 'POST':
        # Extract data from the form
        employee_id = request.POST['employeeId']
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        username = request.POST['username']
        password = request.POST['password']  # Get the raw password
        department_id = request.POST['department_name']  # Assuming department is passed as ID

        # Create a new Employee instance with hashed password
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=make_password(password),  # Hash the password before saving
            department_name_id=department_id  # Use the department ID here
        )
        
        # Save the employee to the database
        employee.save()

        # Redirect to the employee list page or a success page
        return redirect('signin')  # Adjust this to your actual success page

    # If GET request, fetch all departments to display in the form
    departments = Department.objects.all()

    context = {
        "departments": departments  # Use a plural name for clarity
    }
    
    return render(request, 'add_employee.html', context)

def checkin(request):
    if request.method == 'POST':
        employee_input = request.POST.get('employee_input')  # This can be either ID or name

        # Try to find the employee by ID or by name (last_name, first_name)
        try:
            employee = Employee.objects.get(employee_id=employee_input)
        except Employee.DoesNotExist:
            try:
                first_name, last_name = employee_input.split()  # Expecting "Last First"
                employee = Employee.objects.get(first_name__iexact=first_name, last_name__iexact=last_name)
            except (Employee.DoesNotExist, ValueError):
                return HttpResponse("Employee not found.", status=404)

        now_utc = timezone.now()
        philippine_tz = pytz.timezone('Asia/Manila')
        now_philippine = now_utc.astimezone(philippine_tz)

        current_time = now_philippine.time()
        current_date = now_philippine.date()

        # Check attendance record for today
        attendance, created = Attendance.objects.get_or_create(employee=employee, date=current_date)

        # If it's before 12 PM
        if current_time < timezone.datetime.strptime('12:00', '%H:%M').time():
            # If attendance is newly created (no check-in yet)
            if created:
                if current_time < timezone.datetime.strptime('08:10', '%H:%M').time():
                    attendance.arrival_status = 'ontime'
                elif current_time < timezone.datetime.strptime('11:00', '%H:%M').time():
                    attendance.arrival_status = 'late'
                else:
                    attendance.arrival_status = 'absent'  # Mark as absent if they don't check in
                attendance.time_in = current_time
                attendance.save()
                return render(request, 'checkin.html', {'alert_message': 'Attendance marked successfully!'})
            else:
                return HttpResponse("You have already marked your attendance for today.", status=400)

        # If it's 12 PM or later, check if they can mark time out
        if current_time >= timezone.datetime.strptime('12:00', '%H:%M').time():
            if attendance.time_out is None:  # Check if they haven't already timed out
                attendance.time_out = current_time

                # Determine timeout status
                if current_time < timezone.datetime.strptime('17:00', '%H:%M').time():
                    attendance.timeout_status = 'left early'
                elif current_time < timezone.datetime.strptime('19:00', '%H:%M').time():
                    attendance.timeout_status = 'ontime'
                else:
                    attendance.timeout_status = 'overtime'

                attendance.save()
                return render(request, 'checkin.html', {'alert_message': 'Time out marked successfully!'})
            else:
                return HttpResponse("You have already marked your time out for today.", status=400)

    # Handle GET request
    return render(request, 'checkin.html')

@login_required
def admin_dashboard_view(request):
    # Get today's date
    today = timezone.now().date()
    
    # Fetch attendance records for today
    attendance_records = Attendance.objects.filter(date=today)

    context = {
        'attendance_records': attendance_records
    }
    
    return render(request, 'admin_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting login with Username: {username}")  # Log only the username for security
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"User {username} logged in successfully.")  # Success message
            return redirect('admin_dashboard')
        else:
            print("Login failed")  # Debugging
            return HttpResponse("Invalid login credentials. Please try again.")
    
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    return render(request, 'login.html')

# @login_required
# def departments(request):
#     # Get the date from the request, or use today's date if not provided
#     date_str = request.GET.get('date', timezone.now().date().isoformat())
#     selected_date = timezone.datetime.fromisoformat(date_str).date()

#     departments = Department.objects.annotate(
#         employee_count=Count('employees'),
#         late_count=Count('employees', filter=Q(employees__attendance__status='late', employees__attendance__date=selected_date)),
#         absent_count=Count('employees', filter=Q(employees__attendance__status='absent', employees__attendance__date=selected_date)),
#         on_time_count=Count('employees', filter=Q(employees__attendance__status='ontime', employees__attendance__date=selected_date))
#     )
    
#     context = {
#         "departments": departments,  # Use a plural name for clarity
#         "default_date": selected_date,     # Add the selected date to the context
        
#     }
#     return render(request, 'departments.html', context)






# @login_required
# def add_employee(request):
#     if request.method == 'POST':
#         # Extract data from the form
#         employee_id = request.POST['employeeId']
#         first_name = request.POST['firstName']
#         last_name = request.POST['lastName']
#         department_id = request.POST['department_name']  # Assuming department is passed as ID

#         # Create a new Employee instance
#         employee = Employee(
#             employee_id=employee_id,
#             first_name=first_name,
#             last_name=last_name,
#             department_name_id=department_id  # Use the department ID here
#         )
        
#         # Save the employee to the database
#         employee.save()

#         # Redirect to the employee list page or a success page
#         return redirect('employeelist')  # Adjust this to your actual success page

#     # If GET request, fetch all departments to display in the form
#     departments = Department.objects.all()

#     context = {
#         "departments": departments  # Use a plural name for clarity
#     }
    
#     return render(request, 'add_employee.html', context)

@login_required
def attendance_record(request):
    return render(request, 'attendance_record.html')

@login_required
def employeelist(request):
    employee = Employee.objects.all()
    context = {
        "employee": employee
 }
    return render(request, 'employeelist.html', context)



def get_selected_date(request):
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    return timezone.datetime.fromisoformat(date_str).date()


@login_required
def departments(request):
    selected_date = get_selected_date(request)

    departments = Department.objects.annotate(
        late_count=Count('employees', filter=Q(employees__attendance__arrival_status='late', employees__attendance__date=selected_date)),
        absent_count=Count('employees', filter=Q(employees__attendance__arrival_status='absent', employees__attendance__date=selected_date)),
        on_time_count=Count('employees', filter=Q(employees__attendance__arrival_status='ontime', employees__attendance__date=selected_date))
    )
    
    context = {
        "departments": departments,
        "default_date": selected_date,
    }
    return render(request, 'departments.html', context)

@login_required
def viewdepartment(request, department_id):
    department = Department.objects.get(id=department_id)
    selected_date = get_selected_date(request)
    
    employees = Employee.objects.filter(department_name=department)
    attendance_records = Attendance.objects.filter(employee__in=employees, date=selected_date)
   
    return render(request, 'viewdepartments.html', {
        'department': department,
        'employees': employees,
        'attendance_records': attendance_records,
        'default_date': selected_date,
    })



# def get_today_attendance(employee_id):

#     today = timezone.now().date()

#     attendance = Attendance.objects.filter(employee_id=employee_id, date=today)

#     if attendance.exists():

#         return attendance.first()

#     else:

#         return None
    
# @login_required
# def viewdepartment(request, department_id):
#     # Fetch the department based on the provided department_id
#     department = Department.objects.get(id=department_id)
    
#     # Get all employees associated with the department
#     employees = Employee.objects.filter(department_name_id=department_id)
    
#     # Initialize an empty dictionary to store attendance data
#     attendance_data = {}
    
#     # Loop through each employee and get their attendance for today
#     for employee in employees:

#         attendance = get_today_attendance(employee.id)

#         if attendance:

#             attendance_data[employee.id] = {

#                 'status': attendance.status,

#                 'time': attendance.time,

#             }

#         else:

#             attendance_data[employee.id] = {

#                 'status': 'not yet marked',

#                 'time': 'not yet marked',

#             }
    
#     # Render the template with the department, employees, and attendance data
#     return render(request, 'viewdepartments.html', {
#         'department': department,
#         'employees': employees,
#         'attendance_data': attendance_data,
#     })

