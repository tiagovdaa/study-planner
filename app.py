import csv
from flask import Flask, request, render_template, jsonify, send_file
from datetime import datetime, timedelta
from ics import Calendar, Event
import os
from fpdf import FPDF

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def read_courses_from_csv(file_path):
    courses = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['type'] == 'course':
                courses.append({
                    "name": row['name'],
                    "type": "course",
                    "duration_hours": float(row['duration_hours'])
                })
            elif row['type'] == 'book':
                total_pages = int(row['total_pages'])
                duration_hours = total_pages / 60  # 1 page per minute = 60 pages per hour
                courses.append({
                    "name": row['name'],
                    "type": "book",
                    "duration_hours": duration_hours
                })
    return courses

def get_next_weekday(date, weekday):
    """
    Return the next occurrence of the given weekday (0=Monday, 6=Sunday) from a given date.
    """
    days_ahead = weekday - date.weekday()
    if days_ahead < 0 or (days_ahead == 0 and date.time() > datetime.now().time()):  # Handle starting today if within available time
        days_ahead += 7
    return date + timedelta(days_ahead)

def organize_by_time_and_day(events):
    schedule = {}
    # Only create slots for the times that have events
    for event in events:
        start_time_str = event['start'].strftime("%H:00")  # Round down to the nearest hour
        if start_time_str not in schedule:
            schedule[start_time_str] = {day: "" for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        schedule[start_time_str][event['day']] = event['course']

    return schedule

@app.route("/load-csv", methods=["POST"])
def load_csv():
    if 'file' not in request.files:
        return jsonify({"courses": []})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"courses": []})

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Read the courses from the CSV
        courses = read_courses_from_csv(file_path)

        return jsonify({"courses": courses})

    return jsonify({"courses": []})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Process available time for each selected day
            selected_days = request.form.getlist("days[]")
            day_time_slots = {}
            current_date = datetime.now()

            days_of_week = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6
            }

            for day in selected_days:
                start_time_str = request.form.get(f"{day}_start")
                end_time_str = request.form.get(f"{day}_end")
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                # Get the next occurrence of the selected day (allow starting from today if within the available time range)
                if datetime.now().time() < start_time and days_of_week[day] == current_date.weekday():
                    study_day = current_date
                else:
                    study_day = get_next_weekday(current_date, days_of_week[day])

                # Combine date with the time for start and end times
                start_datetime = datetime.combine(study_day, start_time)
                end_datetime = datetime.combine(study_day, end_time)

                available_time_hours = (end_datetime - start_datetime).seconds / 3600
                day_time_slots[day] = {"start": start_datetime, "end": end_datetime, "available_hours": available_time_hours}

            # Process effort percentages
            total_effort = 0
            effort_allocations = {}
            courses = read_courses_from_csv(file_path)

            for course in courses:
                effort_percentage = float(request.form.get(f"{course['name']}_effort", 0))
                total_effort += effort_percentage
                effort_allocations[course['name']] = effort_percentage

            if total_effort != 100:
                return "Error: The total effort percentage must equal 100."

            # Split available time based on effort percentages for each day
            study_plan = []
            for day, time_slot in day_time_slots.items():
                start_time = time_slot["start"]
                available_time_hours = time_slot["available_hours"]

                for course_name, effort_percentage in effort_allocations.items():
                    course_time = available_time_hours * (effort_percentage / 100)
                    study_plan.append({
                        "course": course_name,
                        "start": start_time,
                        "end": start_time + timedelta(hours=course_time),
                        "day": day.capitalize()
                    })
                    start_time += timedelta(hours=course_time)  # Move the start time for the next course

            schedule = organize_by_time_and_day(study_plan)

            # Determine the file type to generate (ics, calendar csv, or pdf)
            file_type = request.form.get("fileType", "ics")
            if file_type == "ics":
                ics_file = generate_ics_calendar(study_plan)
                return send_file(ics_file, as_attachment=True, download_name="study_schedule.ics")
            elif file_type == "google":
                csv_file = generate_calendar_csv(schedule)
                return send_file(csv_file, as_attachment=True, download_name="study_schedule.csv")
            else:
                pdf_file = generate_pdf_schedule(schedule)
                return send_file(pdf_file, as_attachment=True, download_name="study_schedule.pdf")

    return render_template("index.html")

def generate_ics_calendar(events):
    calendar = Calendar()
    for event in events:
        e = Event()
        e.name = f"{event['course']} ({event['day']})"
        e.begin = event['start']
        e.end = event['end']
        calendar.events.add(e)

    file_path = 'study_schedule.ics'
    with open(file_path, 'w') as f:
        f.writelines(calendar)
    return file_path

def generate_calendar_csv(schedule):
    file_path = 'study_schedule.csv'
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Add header row with weekdays
        writer.writerow(["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        # Write each time slot that has subjects and the courses for each day
        for time, days in schedule.items():
            row = [time] + [days[day] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
            if any(row[1:]):  # Only include rows that have at least one subject
                writer.writerow(row)
    
    return file_path

def generate_pdf_schedule(schedule):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Study Schedule", ln=True, align="C")

    # Add table headers with wider columns for text
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 10, txt="Time", border=1, align="C")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        pdf.cell(35, 10, txt=day, border=1, align="C")
    pdf.ln()

    # Add table rows with schedule details, wrapping text if it exceeds the cell width
    pdf.set_font("Arial", "", 10)
    for time, days in schedule.items():
        row_data = [days[day] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
        if any(row_data):  # Only include rows that have at least one subject
            pdf.cell(30, 10, txt=time, border=1)
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                pdf.multi_cell(35, 10, txt=days[day], border=1, align="C")
            pdf.ln()

    file_path = 'study_schedule.pdf'
    pdf.output(file_path)
    return file_path

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host="0.0.0.0", port=5000, debug=True)