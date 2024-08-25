# settings.py
import base64
import os
import logging
import uuid
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.management import BaseCommand
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_backends, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from psycopg2.extras import RealDictCursor

from .forms import AdminForm, AdminLoginForm, Upload_timetable_form, MachineForm,Upload_registered_students
from datetime import datetime
import psycopg2

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, request

import csv
import pandas as pd
from django.core.cache import cache  # Assuming Django's default caching framework is used


# Create your views here.
def index(request):
    return render(request, 'index.html')


def student(request):
    return render(request, 'student.html')


def admin(request):
    return render(request, 'admin.html')


def success_url(request):
    return render(request, 'success_url.html')


def dashboard(request):
    return render(request, 'dashboard.html', {'admin_name': request.session.get('admin_name')})


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def success_url(request):
    return render(request, 'success_url.html')


def admin_login(request):
    return render(request, 'admin_login.html')


def time_table(request):
    return render(request, 'time_table.html')


# views.py

# views.py

def admin_register(request):
    if request.method == 'POST':
        print("Form submitted with POST method")
        form = AdminForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            admin = form.save(commit=False)
            admin.set_password(form.cleaned_data['admin_password'])
            admin.save()

            # Get the backend used for authentication
            backend = get_backends()[0]
            admin.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            login(request, admin, backend=admin.backend)
            messages.success(request, 'Account created successfully')
            return redirect('admin_login')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = AdminForm()
    return render(request, 'admin_register.html', {'form': form})


# views.py


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            try:
                print("Form data (cleaned):", form.cleaned_data)
                ad_email = form.cleaned_data['admin_email']
                ad_password = form.cleaned_data['admin_password']
                admin = authenticate(request, username=ad_email, password=ad_password)
                print("Admin object:", admin)
                if admin is not None:
                    login(request, admin)

                    # Set session data
                    request.session['admin_id'] = admin.id
                    request.session['admin_email'] = admin.admin_email
                    request.session['admin_name'] = f"{admin.admin_fname} {admin.admin_lname}"

                    messages.success(request, 'Login successful')
                    return redirect('dashboard')  # Ensure 'dashboard' is defined in your urls.py
                else:

                    messages.error(request, 'Invalid email or password')
            except KeyError as e:
                print(f"KeyError: {e}")
                messages.error(request, 'Form data error')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Invalid form submission')
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})


# logout view
def admin_logout(request):
    logout(request)
    request.session.flush()  # Clear the session
    return redirect('admin_login')

    # DAPN TIMTABLE UPLOADS


def upload_DAP_timetable(request):
    if request.method == 'POST':
        form = Upload_timetable_form(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            df = pd.read_excel(file, engine='openpyxl')
            current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # SAVE THE DATAFRAME TO  A FOLDER

            filename = f'DAP/TimeTable{current_date}.csv'
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            df.to_csv(file_path, index=False)

            messages.success(request, 'Timetable uploaded successfully')
        else:
            messages.error(request, 'Invalid form submission XLSX file required')

    else:
        form = Upload_timetable_form()

    return render(request, 'time_table.html', {'form': form})


# view DAP uploaded timetable

def view_timetable(request):
    # Path to the "timetables" folder

    DAP_folder = os.path.join(settings.MEDIA_ROOT, 'DAP')

    # Ensure the "timetables" directory exists
    if not os.path.exists(DAP_folder):
        messages.error(request, 'No attendance records uploaded yet')
        return render(request, 'timetable_view.html')

    files = os.listdir(DAP_folder)

    # Filter out files that are not CSV files
    csv_files = [file for file in files if file.endswith('.csv')]

    if not csv_files:
        messages.error(request, 'No CSV files found in the directory')
        return render(request, 'timetable_view.html')

    # Find the most recent file based on the modification time
    most_recent_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(DAP_folder, x)))

    # Read the most recent CSV file
    most_recent_file_path = os.path.join(DAP_folder, most_recent_file)
    df = pd.read_csv(most_recent_file_path)

    timetable_data = df.to_dict(orient='records')
    return render(request, 'timetable_view.html', {'timetable_data': timetable_data})


# ATTENDANCE RECORDS FROM MACHINE
def machine_attendance_upload(request):
    if request.method == 'POST':
        form = Upload_timetable_form(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']

            df = pd.read_excel(file, engine='openpyxl')
            current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # SAVE THE DATAFRAME TO  A FOLDER

            filename = f'timetables/machineattend{current_date}.csv'
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            df.to_csv(file_path, index=False)

            # Save DataFrame to CSV file
            df.to_csv(file_path, index=False)
            return redirect('success_url')
            #messages.success(request, 'File uploaded successfully')
            #print(f'File saved to {file_path}')  # Debug print


        else:
            #  print(form.errors)  # Debug print for form errors
            messages.error(request, 'Invalid form submission. XLSX file required.')
    else:
        form = MachineForm()

    return render(request, 'machine_attendance.html', {'form': form})


def machine_upload_view(request):
    timetables_folder = os.path.join(settings.MEDIA_ROOT, 'timetables')

    # Ensure the "timetables" directory exists
    if not os.path.exists(timetables_folder):
        messages.error(request, 'No attendance records uploaded yet')
        return render(request, 'machine_upload_view.html')

    files = os.listdir(timetables_folder)

    # Filter out files that are not CSV files
    csv_files = [file for file in files if file.endswith('.csv')]

    if not csv_files:
        messages.error(request, 'No CSV files found in the directory')
        return render(request, 'machine_upload_view.html')

    # Find the most recent file based on the modification time
    most_recent_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(timetables_folder, x)))

    # Read the most recent CSV file
    most_recent_file_path = os.path.join(timetables_folder, most_recent_file)
    df = pd.read_csv(most_recent_file_path)

    machine_data = df.to_dict(orient='records')
    return render(request, 'machine_upload_view.html', {'machine_data': machine_data})


# processsing attendance records for quality assurance

def quality_assurance_report(request):
    timetables_folder = os.path.join(settings.MEDIA_ROOT, 'timetables')
    DAP_folder = os.path.join(settings.MEDIA_ROOT, 'DAP')

    # Ensure the "machines records timetables and DAP" directory exists

    if not os.path.exists(timetables_folder) or not os.path.exists(DAP_folder):
        messages.error(request, 'No attendance records uploaded yet')
        return render(request, 'student_attendance_report.html')

    # List CSV files in both directories
    machine_files = [f for f in os.listdir(timetables_folder) if f.endswith('.csv')]
    DAP_files = [f for f in os.listdir(DAP_folder) if f.endswith('.csv')]

    if not machine_files and not DAP_files:
        messages.error(request, 'No CSV files found in the directory')
        return render(request, 'student_attendance_report.html')

    # Find the most recent file based on the modification time
    most_recent_file_machine = max(machine_files, key=lambda x: os.path.getmtime(os.path.join(timetables_folder, x)))
    most_recent_file_DAP = max(DAP_files, key=lambda x: os.path.getmtime(os.path.join(DAP_folder, x)))

    # Read the most recent CSV file
    most_recent_file_path_machine = os.path.join(timetables_folder, most_recent_file_machine)
    most_recent_file_path_DAP = os.path.join(DAP_folder, most_recent_file_DAP)
    df_machine = pd.read_csv(most_recent_file_path_machine)
    df_DAP = pd.read_csv(most_recent_file_path_DAP)

    # Merge the two dataframes; machine data nad DAP  on the 'venue' column
    df_merged = pd.merge(df_machine, df_DAP, on='venue')

    # Save the merged DataFrame to a new CSV file

    current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'QUALITYASSURANCE/student_merged_attendance_report{current_date}.csv'
    student_attend_merged_file_path = os.path.join(settings.MEDIA_ROOT, filename)
    df_merged.to_csv(student_attend_merged_file_path, index=False)

    # Return the merged DataFrame as a dictionary
    student_attend_merged_data_dict = df_merged.to_dict(orient='records')
    return render(request, 'student_attendance_report.html',
                  {'student_attend_merged_data': student_attend_merged_data_dict})


logger = logging.getLogger(__name__)

# Consolidated CSV reading function
import csv

# MAKING NEW CHANGES TO THE VIEWS.PY FILE
# functions to import the courses csv files

import csv


def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, 'r', encoding='latin-1') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                data_list.append(row[0])  # Append the first column value
    return data_list


# Read each departments and course codes and convert them to a list for department map
def read_department_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_computer_science_courses_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_history_courses_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_economics_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_accounting_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_mass_comm_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_electrical_engr_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_computer_engr_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_pharmacy_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_chemistry_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_education_mgt_csv_to_list(file_path):
    return read_csv_to_list(file_path)


def read_political_science_csv_to_list(file_path):
    return read_csv_to_list(file_path)


# course path to directory
attend_gen_data = os.path.join(settings.MEDIA_ROOT, 'attendance_gen_data')
departments_csv_path = os.path.join(attend_gen_data, 'departments.csv')
computer_science_courses_csv_path = os.path.join(attend_gen_data, 'computer_sci_courses.csv')
computer_engr_courses_csv_path = os.path.join(attend_gen_data, 'comp_engr_courses.csv')
electrical_engr_courses_csv_path = os.path.join(attend_gen_data, 'elect_elcetric_engr.csv')
mass_comm_courses_csv_path = os.path.join(attend_gen_data, 'mass_comm.csv')
economics_courses_csv_path = os.path.join(attend_gen_data, 'economics_courses.csv')
accounting_courses_csv_path = os.path.join(attend_gen_data, 'account_courses.csv')
education_mgt_courses_csv_path = os.path.join(attend_gen_data, 'edu_mgt_courses.csv')
chemistry_courses_csv_path = os.path.join(attend_gen_data, 'chemistry_courses.csv')
history_courses_csv_path = os.path.join(attend_gen_data, 'hist_inter_rel.csv')
political_science_courses_csv_path = os.path.join(attend_gen_data, 'political_sci_course.csv')

# course codes conversion to list  for each
computer_sci_course_list = read_computer_science_courses_csv_to_list(computer_science_courses_csv_path)
history_courses_list = read_history_courses_csv_to_list(history_courses_csv_path)
economics_courses_list = read_economics_csv_to_list(economics_courses_csv_path)
accounting_courses_list = read_accounting_csv_to_list(accounting_courses_csv_path)
mass_comm_courses_list = read_mass_comm_csv_to_list(mass_comm_courses_csv_path)
electrical_engr_courses_list = read_electrical_engr_csv_to_list(electrical_engr_courses_csv_path)
computer_engr_courses_list = read_computer_engr_csv_to_list(computer_engr_courses_csv_path)
chemistry_course_list = read_chemistry_csv_to_list(chemistry_courses_csv_path)
education_mgt_course_list = read_education_mgt_csv_to_list(education_mgt_courses_csv_path)
political_science_course_list = read_political_science_csv_to_list(political_science_courses_csv_path)

departments_list = read_department_csv_to_list(departments_csv_path)

levels_list = [100, 200, 300, 400, 500]

department_course_map = {
    "Political Science and Diplomacy": political_science_course_list,
    "Economics": economics_courses_list,
    "Industrial Chemistry": ["IC101", "IC102", "IC201"],
    "Physics with Electronics": ["PWE101", "PWE102", "PWE201"],
    "Applied Microbiology": ["AM101", "AM102", "AM201"],
    "Philosophy": ["PHI101", "PHI102", "PHI201"],
    "Computer Science": computer_sci_course_list,
    "Mass Communication": mass_comm_courses_list,
    "English and Literary Studies": ["ELS101", "ELS102", "ELS201"],
    "History and International Relations": history_courses_list,
    "Marketing and Advertising": ["MA101", "MA102", "MA201"],
    "Accounting": accounting_courses_list,
    "Theology": ["THE101", "THE102", "THE201"],
    "English Education": ["EE101", "EE102", "EE201"],
    "Economics Education": ["EDE101", "EDE102", "EDE201"],
    "Chemistry Education": ["CE101", "CE102", "CE201"],
    "Physics Education": ["PE101", "PE102", "PE201"],
    "Educational Management": education_mgt_course_list,
    "Business Administration": ["BA101", "BA102", "BA201"],
    "Entrepreneurial Studies": ["ES101", "ES102", "ES201"],
    "Peace And Conflict Studies": ["PACS101", "PACS102", "PACS201"],
    "B.Eng Computer Engineering": computer_engr_courses_list,
    "B.Eng Electrical and Electronic Engineering": electrical_engr_courses_list,
    "Law": ["LAW101", "LAW102", "LAW201"],
    "SOFTWARE ENGINEERING": ["SE101", "SE102", "SE201"],
    "Nursing": ["NUR101", "NUR102", "NUR201"],
    "Pharmacy": ["PHAR101", "PHAR102", "PHAR201"],
    "Medical Laboratory Sciences": ["MLS101", "MLS102", "MLS201"],
    "Sacred Theology": ["ST101", "ST102", "ST201"],
    "Computer science Education": ["CSE101", "CSE102", "CSE201"],
    "Medicine and Surgery": ["MS101", "MS102", "MS201"],
    "Religious Education": ["RE101", "RE102", "RE201"],
    "Public Administration": ["PA101", "PA102", "PA201"],
}


def select_course(request):
    return render(request, 'select_course.html')


@csrf_exempt
def get_courses(request, department):
    courses = department_course_map.get(department, [])
    return JsonResponse({'courses': courses})


@csrf_exempt
def process_selection(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        course = request.POST.get('course')
        # Process the selected department and course
        return JsonResponse({'department': department, 'course': course})


@csrf_exempt
def process_selection(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        course = request.POST.get('course_code')
        level = request.POST.get('Level')  # Ensure this matches the form field name exactly

        request.session['department'] = department
        request.session['course'] = course
        request.session['Level'] = level

        try:
            level_int = int(level) if level is not None else 0  # Assuming 0 as a default, adjust as needed
        except ValueError:
            level_int = 0  # Default if conversion fails
            messages.error(request, "Invalid level value. Using default.")

        try:
            filtered_data = load_and_filter_data(department, level_int, course)
            return render(request, 'student_attendance_report.html', {'filtered_data': filtered_data})
        except Exception as e:
            messages.error(request, str(e))
            # If an error occurs, still render the page but without filtered_data
            return render(request, 'student_attendance_report.html',
                          {'department': department, 'course': course, 'level': level})
    # If not POST, or after handling POST, render a default or error page
    return render(request, 'some_default_or_error_page.html')


# upload department and course codes


def generate_attendance(request):
    # Assuming these are set earlier in the function
    department = request.session.get('department')
    course = request.session.get('course')
    level_int = int(request.session.get('level', 0))  # Default to 0 if not set

    try:
        # Assuming 'load_and_filter_data' returns a DataFrame
        filtered_data = load_and_filter_data(department, level_int, course)

        # Render the page with the filtered data
        return render(request, 'student_attendance_report.html',
                      {'filtered_data': filtered_data.to_dict(orient='records')})

    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'student_attendance_report.html')


# update comp_sci_100l table wth filtered data


def load_and_filter_data(department, level, course_code):
    column_types = {
        'ID': str, 'Name': str, 'Dept': str, 'Userprofile': str, 'SN': int,
        'Coursetitle': str, 'CourseCode': str, 'Level': int,
    }
    quality_folder = os.path.join(settings.MEDIA_ROOT, 'QUALITYASSURANCE')
    most_recent_file = max(
        os.listdir(quality_folder),
        key=lambda x: os.path.getmtime(os.path.join(quality_folder, x))
    )
    most_recent_file_path = os.path.join(quality_folder, most_recent_file)

    # Use on_bad_lines='skip' to skip lines with too many fields
    df = pd.read_csv(most_recent_file_path, delimiter=',', dtype=column_types, engine='python', encoding='latin-1')

    # Print the first few rows of the DataFrame
    print("First few rows of the DataFrame:")
    print(df.head())

    # Debug: Print unique values in Dept and CourseCode columns
    print("\nUnique values in Dept column before stripping and uppercasing:")
    print(df['Dept'].unique())
    print("Unique values in CourseCode column before stripping and uppercasing:")
    print(df['CourseCode'].unique())

    # Strip and uppercase the filter values
    department = department.strip().upper()
    course_code = course_code.strip().upper()

    # Intermediate filtering steps
    dept_filtered = df['Dept'].str.strip().str.upper() == department
    level_filtered = df['Level'] == level
    course_code_filtered = df['CourseCode'].str.strip().str.upper() == course_code

    print("\nDepartment variable after stripping and uppercasing:", department)
    print("Course code variable after stripping and uppercasing:", course_code)

    # Print the intermediate filter results
    print("\nDept Filter Result:")
    print(dept_filtered)
    print("Level Filter Result:")
    print(level_filtered)
    print("Course Code Filter Result:")
    print(course_code_filtered)

    # Apply the filters
    filtered_df = df[dept_filtered & level_filtered & course_code_filtered]

    print("Filtered DataFrame is empty:", filtered_df.empty)
    print("Filtered DataFrame:")
    print(filtered_df)

    # SAVE FILTERED DATA TO A CSV FILE IN THE FILTERED_DATA FOLDER BY DEPARTMENT AND LEVEL
    # Check if the department and level match specific criteria
    if department == 'Computer Science'.upper() and level == 100:
        # Assuming 'course_code' and 'filtered_df' are defined
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_dir = os.path.join(settings.MEDIA_ROOT, 'WEEKLY_ATTENDANCE/computer_science/100l')
        filename = f'FILTERED_DATA/computer_sci/100l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Check if the file already exists
        if os.path.exists(file_path):
            # Read the existing data
            existing_df = pd.read_csv(file_path)

            # Check if 'attendance_score' column exists in the new data
            if 'attendance_score' not in filtered_df.columns:
                # Initialize 'attendance_score' in new data if it doesn't exist
                filtered_df['attendance_score'] = 1

            # Merge the new data with the existing data
            # Assuming 'student_id' is the unique identifier
            merged_df = pd.merge(existing_df, filtered_df, on='Userprofile', how='outer')


            # Update 'attendance_score' in the merged DataFrame
            # This logic may need to be adjusted based on how you want to calculate the updated scores
            merged_df['attendance_score'] = merged_df['attendance_score_x'].fillna(0) + merged_df[
                'attendance_score_y'].fillna(1)

            # Drop the extra columns created by the merge operation
            merged_df.drop(columns=['attendance_score_x', 'attendance_score_y'], inplace=True)

            # Save the merged DataFrame back to the same file
            merged_df.to_csv(file_path, index=False)
            print(merged_df.head())


        else:
                # If the file doesn't exist, simply save the new data
                # Initialize 'attendance_score' if it doesn't exist
                if 'attendance_score' not in filtered_df.columns:
                    filtered_df['attendance_score'] = 1
    
                filtered_df.to_csv(file_path, index=False)
                print(f'File saved to {file_path}')
                


    elif department == 'Computer Science'.upper() and level == 200:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/computer_sci200l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        filtered_df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

    elif department == 'Computer Science'.upper() and level == 400:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/computer_sci200l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # add the colum to serve as attendance score Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        filtered_df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

        # SAME THING FOR Political Science and Diplomacy department
    elif department == 'Political Science and Diplomacy'.upper() and level == 100:
        unique_id = uuid.uuid4()
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/political_sci/100l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # add the colum to serve as attendance score Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

    elif department == 'Political Science and Diplomacy'.upper() and level == 200:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/political_sci/200l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # add the colum to serve as attendance score Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        filtered_df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

    elif department == 'Political Science and Diplomacy'.upper() and level == 300:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/political_sci/300l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # add the colum to serve as attendance score Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        filtered_df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

    elif department == 'Political Science and Diplomacy'.upper() and level == 400:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'FILTERED_DATA/political_sci/400l/{course_code}_{current_date}.csv'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # add the colum to serve as attendance score Save the DataFrame to a CSV file
        filtered_df['attendance_score'] = 1
        filtered_df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')

    else:
        print("Invalid department, level, or course code.")
    if filtered_df.empty:
        raise ValueError('No data found for the given department, level, and course code')

    filtered_data = filtered_df.to_dict(orient='records')
    weekly_attendance()
    return filtered_data


# UNSCHEDULED EVENTS ATTENDANCE PROCESSING CAPTURED BY MACHINE HANDLING
def unscheduled_events_attendance(request):
    return render(request, 'unscheduled_events.html')


# TRACKING  ATTENDANCE CRITERIA FOR SELCETING DEPT, COURSE AND LEVEL

@csrf_exempt
def track_attendance(request):
    if request.method == 'POST':
        department = request.POST.get('department1')
        course = request.POST.get('course_code')
        level = request.POST.get('Level')
        matric_num = request.POST.get('matric_num')
        # Ensure this matches the form field name exactly

        request.session['department'] = department
        request.session['course'] = course
        request.session['Level'] = level
        request.session['matric_num'] = matric_num

        try:
            level_int = int(level) if level is not None else 0  # Assuming 0 as a default, adjust as needed
        except ValueError:
            level_int = 0  # Default if conversion fails
            messages.error(request, "Invalid level value. Using default.")

        try:
            filtered_data = load_and_filter_data(department, level_int, course)
            return render(request, 'summary_attend.html', {'filtered_data': filtered_data})
        except Exception as e:
            messages.error(request, str(e))
            # If an error occurs, still render the page but without filtered_data
            return render(request, 'summary_attend.html',
                          {'department': department, 'course': course, 'level': level})
    else:
        # If not POST, or after handling POST, render a default or error page
        return render(request, 'some_default_or_error_page.html')



def weekly_attendance():
    folder_path = 'DAP/FILTERED_DATA/computer_sci/100l'
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    dataframes = [pd.read_csv(os.path.join(folder_path, file), low_memory=False) for file in csv_files]
    cleaned_dataframes = [df.dropna(axis=1, how='all') for df in dataframes]
    merged_df = pd.concat(cleaned_dataframes)

    summed_df = merged_df.groupby('Userprofile')['attendance_score'].sum().reset_index()

    current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_dir = os.path.join(settings.MEDIA_ROOT, 'WEEKLY_ATTENDANCE/computer_science')
    os.makedirs(file_dir, exist_ok=True)
    filename = f'comp_sci_100_{current_date}.csv'
    file_path = os.path.join(file_dir, filename)
    summed_df.to_csv(file_path, index=False)

    comp_sci_100l_students = [f for f in os.listdir(file_dir) if f.endswith('.csv')]
    most_recent_file = max(comp_sci_100l_students, key=lambda f: os.path.getmtime(os.path.join(file_dir, f)))

    most_recent_tot_score_path_comp_sci_100l = os.path.join(file_dir, most_recent_file)
    df_comp_sci_100l = pd.read_csv(most_recent_tot_score_path_comp_sci_100l)

    if df_comp_sci_100l.empty:
        print("DataFrame is empty. No data to update.")
        return

    print("File uploaded and processed successfully NOW.")
    print(df_comp_sci_100l.head())

    conn = psycopg2.connect(
        dbname='ettend_db',
        user='postgres',
        password='blaze',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()

    for index, row in df_comp_sci_100l.iterrows():
        query = """
        UPDATE ettend_db.public.attendance_proj_comp_sci_100l
        SET 
            total_attendance_score = %s,
            week = %s
        WHERE matric_num = %s
        """
        print(cur.mogrify(query, (row["attendance_score"], 1, row['Userprofile'])))
        cur.execute(query, (row["attendance_score"], 1, row['Userprofile']))
        print(f"Rows updated: {cur.rowcount}")

    conn.commit()
    cur.close()
    conn.close()
    print("Database updated successfully")







# CREATE THE DATABASE RECORDS OF REGISTRED STUDENTS FROM EACH LEVEL IN A DEPARTMENT FROM CSV FILE UPLOAD
# consider the department and level of the students
# update the database


@csrf_exempt
def Update_weekely_attendance_DB(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        level = request.POST.get('Level')
        form = Upload_registered_students(request.POST, request.FILES)

        conn = psycopg2.connect(
            dbname='ettend_db',
            user='postgres',
            password='blaze',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()

        # Save the uploaded file to a folder
        if form.is_valid():
            if 'file' in form.cleaned_data:
                try:
                    file = form.cleaned_data['file']
                    df = pd.read_excel(file, engine='openpyxl')
                    current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                except Exception as e:
                    messages.error(request, f"An error occurred while processing the file: {e}")



                # List CSV files in the directories
                try:
                    level_int = int(level) if level else 0  # Assuming 0 as a default, adjust as needed
                except ValueError:
                    level_int = 0  # Default if conversion fails
                    messages.error(request, "Invalid level value. Using default.")

                print("debugging: level and dept present in the request", department, level, form.errors)

                # STUDENT RECORDS UPLOAD TO DATABASE
                # COMPUTER SCIENCE 100L STUDENTS ONLY
                if department == 'Computer Science':
                    if level_int == 100:
                        comp_sci_100l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                       'course_registeration/computer_science/100l')
                        comp_sci_100l_students_filename = f'computer_science_100l_{current_date}.csv'
                        comp_sci_100l_students_file_path = os.path.join(comp_sci_100l_students_dir_path,
                                                                        comp_sci_100l_students_filename)

                        df.to_csv(comp_sci_100l_students_file_path, index=False)

                        comp_sci_100l_students = [f for f in os.listdir(comp_sci_100l_students_dir_path) if
                                                  f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(comp_sci_100l_students, key=lambda f: os.path.getmtime(
                            os.path.join(comp_sci_100l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_comp_sci_100l = os.path.join(comp_sci_100l_students_dir_path,
                                                                           most_recent_file)
                        df_comp_sci_100l = pd.read_csv(most_recent_file_path_comp_sci_100l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_comp_sci_100l.head())

                        # Upload most recent file to the computer_sci_100L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_comp_sci_100l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_comp_sci_100l (biometric_id, student_name, "CSC_101", "CSC_102", "CSC_105", "CSC_111", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["CSC101"], row["CSC102"], row["CSC105"],
                                 row["CSC111"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                        conn.commit()
                        cur.close()
                        conn.close()
                        print("Database updated successfully")

                    # COMPUTER SCIENCE 200L STUDENTS ONLY
                    elif level_int == 200:
                        comp_sci_200l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                       'course_registeration/computer_science/200l')
                        comp_sci_200l_students_filename = f'computer_science_200l_{current_date}.csv'
                        comp_sci_200l_students_file_path = os.path.join(comp_sci_200l_students_dir_path,
                                                                        comp_sci_200l_students_filename)

                        df.to_csv(comp_sci_200l_students_file_path, index=False)

                        comp_sci_200l_students = [f for f in os.listdir(comp_sci_200l_students_dir_path) if
                                                  f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(comp_sci_200l_students, key=lambda f: os.path.getmtime(
                            os.path.join(comp_sci_200l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_comp_sci_200l = os.path.join(comp_sci_200l_students_dir_path,
                                                                           most_recent_file)
                        df_comp_sci_200l = pd.read_csv(most_recent_file_path_comp_sci_200l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_comp_sci_200l.head())

                        # Upload most recent file to the computer_sci_200L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_comp_sci_200l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_comp_sci_200l (biometric_id, student_name, "CSC_201", "CSC_202", "CSC_203", "CSC_204", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["CSC201"], row["CSC"], row["CSC203"],
                                 row["CSC204"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")

                    # COMPUTER SCIENCE 300L STUDENTS ONLY
                    elif level_int == 300:
                        comp_sci_300l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                       'course_registeration/computer_science/300l')
                        comp_sci_300l_students_filename = f'computer_science_300l_{current_date}.csv'
                        comp_sci_300l_students_file_path = os.path.join(comp_sci_300l_students_dir_path,
                                                                        comp_sci_300l_students_filename)

                        df.to_csv(comp_sci_300l_students_file_path, index=False)

                        comp_sci_300l_students = [f for f in os.listdir(comp_sci_300l_students_dir_path) if
                                                  f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(comp_sci_300l_students, key=lambda f: os.path.getmtime(
                            os.path.join(comp_sci_300l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_comp_sci_300l = os.path.join(comp_sci_300l_students_dir_path,
                                                                           most_recent_file)
                        df_comp_sci_300l = pd.read_csv(most_recent_file_path_comp_sci_300l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_comp_sci_300l.head())

                        # Upload most recent file to the computer_sci_300L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_comp_sci_300l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_comp_sci_300l (biometric_id, student_name, "CSC_301", "CSC_302", "CSC_303", "CSC_304", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["CSC301"], row["CSC302"], row["CSC303"],
                                 row["CSC304"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close

                            print("Database updated successfully")

                    # COMPUTER SCIENCE 400L STUDENTS ONLY
                    elif level_int == 400:
                        comp_sci_400l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                       'course_registeration/computer_science/400l')
                        comp_sci_400l_students_filename = f'computer_science_400l_{current_date}.csv'
                        comp_sci_400l_students_file_path = os.path.join(comp_sci_400l_students_dir_path,
                                                                        comp_sci_400l_students_filename)

                        df.to_csv(comp_sci_400l_students_file_path, index=False)

                        comp_sci_400l_students = [f for f in os.listdir(comp_sci_400l_students_dir_path) if
                                                  f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(comp_sci_400l_students, key=lambda f: os.path.getmtime(
                            os.path.join(comp_sci_400l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_comp_sci_400l = os.path.join(comp_sci_400l_students_dir_path,
                                                                           most_recent_file)
                        df_comp_sci_400l = pd.read_csv(most_recent_file_path_comp_sci_400l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_comp_sci_400l.head())

                        # Upload most recent file to the computer_sci_400L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_comp_sci_400l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_comp_sci_400l (biometric_id, student_name, "CSC_401", "CSC_402", "CSC_403", "CSC_404", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["CSC401"], row["CSC402"], row["CSC403"],
                                 row["CSC404"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")

                # FOR POLITICAL SCIENCE AND DIPLOMACY DEPARTMENT
                elif department == 'Political Science and Diplomacy':
                    if level_int == 100:
                        political_sci_100l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                          'course_registeration/political_science/100l')
                        political_sci_100l_students_filename = f'political_sci_100l_{current_date}.csv'
                        political_sci_100l_students_file_path = os.path.join(political_sci_100l_students_dir_path,
                                                                           political_sci_100l_students_filename)

                        df.to_csv(political_sci_100l_students_file_path, index=False)

                        political_sci_100l_students = [f for f in os.listdir(political_sci_100l_students_dir_path) if
                                                     f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(political_sci_100l_students, key=lambda f: os.path.getmtime(
                            os.path.join(political_sci_100l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_political_sci_100l = os.path.join(political_sci_100l_students_dir_path,
                                                                            most_recent_file)
                        df_political_sci_100l = pd.read_csv(most_recent_file_path_political_sci_100l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_political_sci_100l.head())

                        # Upload most recent file to the political_sci_100L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_political_sci_100l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_pol_sci_100l (biometric_id, student_name, "POL_101", "POL_102", "POL_103", "POL_104", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["PSC101"], row["PSC102"], row["PSC103"],
                                 row["PSC104"], level_int, 0, 0,row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")

                    # POLITICAL SCIENCE AND DIPLOMACY 200L STUDENTS ONLY
                    elif level_int == 200:
                        political_sci_200l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                          'course_registeration/political_science/200l')
                        political_sci_200l_students_filename = f'political_sci_200l_{current_date}.csv'
                        political_sci_200l_students_file_path = os.path.join(political_sci_200l_students_dir_path,
                                                                           political_sci_200l_students_filename)

                        df.to_csv(political_sci_200l_students_file_path, index=False)

                        political_sci_200l_students = [f for f in os.listdir(political_sci_200l_students_dir_path) if
                                                     f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(political_sci_200l_students, key=lambda f: os.path.getmtime(
                            os.path.join(political_sci_200l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_political_sci_200l = os.path.join(political_sci_200l_students_dir_path,
                                                                            most_recent_file)
                        df_political_sci_200l = pd.read_csv(most_recent_file_path_political_sci_200l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_political_sci_200l.head())

                        # Upload most recent file to the political_sci_200L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_political_sci_200l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_pol_sci_200l (biometric_id, student_name, "POL_201", "POL_202", "POL_203", "POL_204", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["POL201"], row["POL202"], row["POL203"],
                                 row["POL204"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")

                    # POLITICAL SCIENCE AND DIPLOMACY 300L STUDENTS ONLY
                    elif level_int == 300:
                        political_sci_300l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                          'course_registeration/political_science/300l')
                        political_sci_300l_students_filename = f'political_sci_300l_{current_date}.csv'
                        political_sci_300l_students_file_path = os.path.join(political_sci_300l_students_dir_path,
                                                                           political_sci_300l_students_filename)

                        df.to_csv(political_sci_300l_students_file_path, index=False)

                        political_sci_300l_students = [f for f in os.listdir(political_sci_300l_students_dir_path) if
                                                     f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(political_sci_300l_students, key=lambda f: os.path.getmtime(
                            os.path.join(political_sci_300l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_political_sci_300l = os.path.join(political_sci_300l_students_dir_path,
                                                                            most_recent_file)
                        df_political_sci_300l = pd.read_csv(most_recent_file_path_political_sci_300l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_political_sci_300l.head())

                        # Upload most recent file to the political_sci_300L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_political_sci_300l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_pol_sci_300l (biometric_id, student_name, "POL_301", "POL_302", "POL_303", "POL_304", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["POL301"], row["POL302"], row["POL303"],
                                 row["POL304"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")

                    # POLITICAL SCIENCE AND DIPLOMACY 400L STUDENTS ONLY
                    elif level_int == 400:
                        political_sci_400l_students_dir_path = os.path.join(settings.MEDIA_ROOT,
                                                                          'course_registeration/political_science/400l')
                        political_sci_400l_students_filename = f'political_sci_400l_{current_date}.csv'
                        political_sci_400l_students_file_path = os.path.join(political_sci_400l_students_dir_path,
                                                                           political_sci_400l_students_filename)

                        df.to_csv(political_sci_400l_students_file_path, index=False)

                        political_sci_400l_students = [f for f in os.listdir(political_sci_400l_students_dir_path) if
                                                     f.endswith('.csv')]

                        # Find the most recent file based on the modification time
                        most_recent_file = max(political_sci_400l_students, key=lambda f: os.path.getmtime(
                            os.path.join(political_sci_400l_students_dir_path, f)))

                        # Read the most recent CSV file
                        most_recent_file_path_political_sci_400l = os.path.join(political_sci_400l_students_dir_path,
                                                                            most_recent_file)
                        df_political_sci_400l = pd.read_csv(most_recent_file_path_political_sci_400l)
                        messages.success(request, "File uploaded and processed successfully NOW.")
                        print(df_political_sci_400l.head())

                        # Upload most recent file to the political_sci_400L DATABASE

                        # Update the database with the new attendance scores
                        for index, row in df_political_sci_400l.iterrows():
                            cur.execute(
                                """
                                INSERT INTO ettend_db.public.attendance_proj_pol_sci_400l (biometric_id, student_name, "POL_401", "POL_402", "POL_403", "POL_404", level, total_attendance_score, week, matric_num)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (row['BIOMETRICS_ID'], row['STUDENT_NAME'], row["POL401"], row["POL402"], row["POL403"],
                                 row["POL404"], level_int, 0, 0, row['MATRIC_NO.'])
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            print("Database updated successfully")



                else:
                    messages.error(request, "Invalid department or level.")
        else:
            messages.error(request, "Invalid form submission.")

    form = Upload_registered_students()
    return render(request, 'departmental_students_upload.html', {'form': form})


def summary_attendance(request):
    """
    Generates a summary of attendance for a given department, course, and level.
    Renders a page with the filtered attendance data or an error message.

    :param request: HttpRequest object containing session data for department, course, and level.
    :return: HttpResponse object rendering the appropriate template.
    """
    # Retrieve session data with defaults
    department = request.session.get('department', None)
    course = request.session.get('course', None)
    level_int = int(request.session.get('level', 0))  # Default to 0 if not set or found

    try:
        # Validate session data
        if not department or not course:
            raise ValueError("Missing department or course information in session.")

        # Load and filter data based on session parameters
        filtered_data = load_and_filter_data(department, level_int, course)

        # Render the page with the filtered data
        return render(request, 'summary_attend.html', {'filtered_data': filtered_data.to_dict(orient='records')})

    except Exception as e:
        # Log the error and show an error message to the user
        logger.error(f"Error generating attendance summary: {str(e)}")
        messages.error(request, str(e))
        return render(request, 'summary_attend.html')


# GENERATE STUDENTS ATTENDANCE SCORECARD FOR THE WEEK USING STORED RECORDS IN THE DATABASE
# qr code generator to authenticate the student scorecard
# qr code generator to authenticate the student scorecard
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str
def attendance_score_card(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        level = request.POST.get('Level')
        matric_num = request.POST.get('matric_num')

        print(department,level,matric_num)

        try:
            level_int = int(level) if level else 0
        except ValueError:
            level_int = 0

        conn = psycopg2.connect(
            dbname='ettend_db',
            user='postgres',
            password='blaze',
            host='localhost',
            port='5432'
        )


        # for computer science department
        try:
            if department == "Computer Science":
                cur = conn.cursor(cursor_factory=RealDictCursor)
                if level_int == 100:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_comp_sci_100l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 200:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_comp_sci_200l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 300:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_comp_sci_300l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 400:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_comp_sci_400l WHERE matric_num = %s",
                        (matric_num,)
                    )
                else:
                    raise ValueError('Invalid level selected')
                student_data = cur.fetchall()
                for student in student_data:
                    total_possible_score = 15  # or whatever the total possible score is
                    student['attendance_percentage'] = (student['total_attendance_score'] / total_possible_score) * 100
                    student["department"] = department
                    student["absents"] = total_possible_score - student['total_attendance_score']
                    # PERCENTAGE ABSENTS
                    student["absent_percentage"] = (student["absents"] / total_possible_score) * 100
                    # todays date
                    student["date"] = datetime.now().strftime('%Y-%m-%d')
                    qr_data = f"{student['matric_num']} {student['student_name']} {student['attendance_percentage']}"
                    student['qr_code'] = generate_qr_code(qr_data)
                cur.close()
                conn.close()



                if not student_data:
                    raise ValueError('No data found for the given department, level, and matric number')

                return render(request, 'scorecard.html', {'student_data': student_data})

            # for political science department
            elif department == "Political Science and Diplomacy":
                cur = conn.cursor(cursor_factory=RealDictCursor)
                if level_int == 100:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_pol_sci_100l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 200:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_pol_sci_200l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 300:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_pol_sci_300l WHERE matric_num = %s",
                        (matric_num,)
                    )
                elif level_int == 400:
                    cur.execute(
                        "SELECT * FROM ettend_db.public.attendance_proj_pol_sci_400l WHERE matric_num = %s",
                        (matric_num,)
                    )
                else:
                    raise ValueError('Invalid level selected')
                student_data = cur.fetchall()
                for student in student_data:
                    total_possible_score = 15
                    student['attendance_percentage'] = (student['total_attendance_score'] / total_possible_score) * 100
                    student["department"] = department
                    student["absents"] = total_possible_score - student['total_attendance_score']
                    # PERCENTAGE ABSENTS
                    student["absent_percentage"] = (student["absents"] / total_possible_score) * 100
                    # todays date
                    student["date"] = datetime.now().strftime('%Y-%m-%d')
                    qr_data = f"{student['matric_num']} {student['student_name']} {student['attendance_percentage']}"
                    student['qr_code'] = generate_qr_code(qr_data)
                cur.close()
                conn.close()
                if not student_data:
                    raise ValueError('No data found for the given department, level, and matric number')
                return render(request, 'scorecard.html', {'student_data': student_data})

            else:
                raise ValueError('Invalid department selected')

        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'scorecard.html')

    # Return a default response if the request method is not POST
    return render(request, 'scorecard.html')


