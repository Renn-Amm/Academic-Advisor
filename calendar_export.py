"""
Calendar Export and Print Utilities
"""
from datetime import datetime, timedelta
from typing import List
import pandas as pd


def generate_ical_export(enrolled_courses: List, courses_df: pd.DataFrame) -> str:
    """
    Generate iCalendar (.ics) file for enrolled courses
    
    Args:
        enrolled_courses: List of enrolled course IDs
        courses_df: DataFrame with course information
        
    Returns:
        iCalendar format string
    """
    # Start date for courses (assume current date or next Monday)
    start_date = datetime.now()
    days_until_monday = (7 - start_date.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    start_date = start_date + timedelta(days=days_until_monday)
    
    ical_content = []
    ical_content.append("BEGIN:VCALENDAR")
    ical_content.append("VERSION:2.0")
    ical_content.append("PRODID:-//Harbour Space University//AI Academic Advisor//EN")
    ical_content.append("CALSCALE:GREGORIAN")
    ical_content.append("METHOD:PUBLISH")
    ical_content.append("X-WR-CALNAME:My Course Schedule")
    ical_content.append("X-WR-TIMEZONE:UTC")
    
    # Time slot mappings
    time_slots = {
        '9:00 AM - 12:20 PM': {'hour': 9, 'minute': 0, 'end_hour': 12, 'end_minute': 20},
        '1:00 PM - 4:20 PM': {'hour': 13, 'minute': 0, 'end_hour': 16, 'end_minute': 20},
        '5:00 PM - 8:20 PM': {'hour': 17, 'minute': 0, 'end_hour': 20, 'end_minute': 20}
    }
    
    for enrolled_id in enrolled_courses:
        # Parse course ID and mode
        if ':' in str(enrolled_id):
            course_id, mode = str(enrolled_id).split(':')
        else:
            course_id = str(enrolled_id)
            mode = 'enroll'
        
        # Get course details
        course_row = courses_df[courses_df['course_id'] == course_id]
        if course_row.empty:
            continue
            
        course = course_row.iloc[0]
        course_name = course['course_name']
        class_time = course.get('class_time', '9:00 AM - 12:20 PM')
        description = course.get('course_description', 'No description available')
        
        # Get time slot details
        time_info = time_slots.get(class_time, time_slots['9:00 AM - 12:20 PM'])
        
        # Create recurring events for 3 weeks (Mon-Fri)
        for week in range(3):  # 3-week module
            for day in range(5):  # Monday to Friday
                event_date = start_date + timedelta(weeks=week, days=day)
                
                # Create event start and end times
                event_start = event_date.replace(
                    hour=time_info['hour'],
                    minute=time_info['minute'],
                    second=0,
                    microsecond=0
                )
                event_end = event_date.replace(
                    hour=time_info['end_hour'],
                    minute=time_info['end_minute'],
                    second=0,
                    microsecond=0
                )
                
                # Format for iCal
                dtstart = event_start.strftime('%Y%m%dT%H%M%S')
                dtend = event_end.strftime('%Y%m%dT%H%M%S')
                dtstamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
                uid = f"{course_id}-{week}-{day}@harbourspace.edu"
                
                # Add event
                ical_content.append("BEGIN:VEVENT")
                ical_content.append(f"UID:{uid}")
                ical_content.append(f"DTSTAMP:{dtstamp}")
                ical_content.append(f"DTSTART:{dtstart}")
                ical_content.append(f"DTEND:{dtend}")
                ical_content.append(f"SUMMARY:{course_name} ({mode.upper()})")
                ical_content.append(f"DESCRIPTION:{description[:100]}")
                ical_content.append(f"LOCATION:Harbour Space University")
                ical_content.append(f"STATUS:CONFIRMED")
                ical_content.append("END:VEVENT")
    
    ical_content.append("END:VCALENDAR")
    
    return "\n".join(ical_content)


def generate_print_friendly_html(enrolled_courses: List, courses_df: pd.DataFrame) -> str:
    """
    Generate print-friendly HTML schedule
    
    Args:
        enrolled_courses: List of enrolled course IDs
        courses_df: DataFrame with course information
        
    Returns:
        HTML string for printing
    """
    html = """
    <style>
        @media print {
            body { font-family: Arial, sans-serif; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; page-break-inside: avoid; }
            th { background-color: #3498db; color: white; padding: 12px; text-align: left; }
            td { border: 1px solid #ddd; padding: 10px; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .course-info { margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; }
            .time-slot { font-weight: bold; color: #2c3e50; }
            .mode-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .mode-enroll { background-color: #27ae60; color: white; }
            .mode-audit { background-color: #95a5a6; color: white; }
        }
        @page { margin: 2cm; }
    </style>
    <h1>My Course Schedule</h1>
    <p><strong>Generated:</strong> """ + datetime.now().strftime('%B %d, %Y at %H:%M') + """</p>
    
    <h2>Enrolled Courses</h2>
    <table>
        <thead>
            <tr>
                <th>Course Name</th>
                <th>Course ID</th>
                <th>Time Slot</th>
                <th>Mode</th>
                <th>Credits</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for enrolled_id in enrolled_courses:
        # Parse course ID and mode
        if ':' in str(enrolled_id):
            course_id, mode = str(enrolled_id).split(':')
        else:
            course_id = str(enrolled_id)
            mode = 'enroll'
        
        # Get course details
        course_row = courses_df[courses_df['course_id'] == course_id]
        if course_row.empty:
            continue
            
        course = course_row.iloc[0]
        mode_class = f"mode-{mode}"
        
        html += f"""
            <tr>
                <td>{course['course_name']}</td>
                <td>{course['course_id']}</td>
                <td class="time-slot">{course.get('class_time', 'TBD')}</td>
                <td><span class="{mode_class} mode-badge">{mode.upper()}</span></td>
                <td>{course.get('credits', 3)}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    
    <h2>Weekly Schedule</h2>
    <table>
        <thead>
            <tr>
                <th>Time Slot</th>
                <th>Monday - Friday</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Group by time slots
    time_slots = ['9:00 AM - 12:20 PM', '1:00 PM - 4:20 PM', '5:00 PM - 8:20 PM']
    for time_slot in time_slots:
        courses_in_slot = []
        for enrolled_id in enrolled_courses:
            if ':' in str(enrolled_id):
                course_id, mode = str(enrolled_id).split(':')
            else:
                course_id = str(enrolled_id)
                mode = 'enroll'
            
            course_row = courses_df[courses_df['course_id'] == course_id]
            if not course_row.empty:
                course = course_row.iloc[0]
                if course.get('class_time') == time_slot:
                    courses_in_slot.append(f"{course['course_name']} ({mode.upper()})")
        
        courses_str = "<br>".join(courses_in_slot) if courses_in_slot else "No classes"
        html += f"""
            <tr>
                <td class="time-slot">{time_slot}</td>
                <td>{courses_str}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    
    <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d;">
        <p><strong>Note:</strong> Each course runs for 3 weeks (1 module)</p>
        <p><strong>Attendance Policy:</strong> 3+ absences = Automatic Fail | Being 10 min late = 1 absence</p>
        <p><strong>Time Slots:</strong> Morning (9:00-12:20) | Afternoon (1:00-4:20) | Evening (5:00-8:20)</p>
    </div>
    """
    
    return html
