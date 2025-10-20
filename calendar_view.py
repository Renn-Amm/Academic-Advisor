"""
Calendar View Component for Course Schedule Visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict
import streamlit.components.v1 as components
from calendar_export import generate_ical_export, generate_print_friendly_html


def generate_week_calendar(enrolled_courses, courses_df):
    """Generate weekly calendar view of enrolled courses"""
    
    # Define time slots
    time_slots = {
        '9:00 AM - 12:20 PM': {'start': 9, 'end': 12.33, 'slot': 'Morning'},
        '1:00 PM - 4:20 PM': {'start': 13, 'end': 16.33, 'slot': 'Afternoon'},
        '5:00 PM - 8:20 PM': {'start': 17, 'end': 20.33, 'slot': 'Evening'}
    }
    
    # Days of week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Create calendar data
    calendar_data = []
    
    for enrolled_id in enrolled_courses:
        # Parse course_id:mode format
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
        class_time = course.get('class_time', 'TBD')
        
        if class_time in time_slots:
            # Add event for each day of the week
            slot_info = time_slots[class_time]
            for day in days:
                calendar_data.append({
                    'Course': course_name,
                    'Day': day,
                    'Start': slot_info['start'],
                    'End': slot_info['end'],
                    'Slot': slot_info['slot'],
                    'Time': class_time,
                    'Mode': mode.title()
                })
    
    return pd.DataFrame(calendar_data)


def render_calendar_view(enrolled_courses, courses_df):
    """Render interactive calendar view"""
    
    st.markdown("### 📅 Weekly Schedule Calendar")
    
    if not enrolled_courses:
        st.info("No courses enrolled yet. Enroll in courses to see your weekly schedule!")
        return
    
    # Generate calendar data
    calendar_df = generate_week_calendar(enrolled_courses, courses_df)
    
    if calendar_df.empty:
        st.info("No scheduled courses to display.")
        return
    
    # Create Gantt-style timeline chart
    fig = go.Figure()
    
    # Color mapping for time slots
    colors = {
        'Morning': '#3b82f6',
        'Afternoon': '#10b981',
        'Evening': '#f59e0b'
    }
    
    # Add bars for each course
    for idx, row in calendar_df.iterrows():
        fig.add_trace(go.Bar(
            name=row['Course'],
            x=[row['End'] - row['Start']],
            y=[row['Day']],
            base=[row['Start']],
            orientation='h',
            marker=dict(
                color=colors.get(row['Slot'], '#6b7280'),
                line=dict(color='white', width=2)
            ),
            text=f"{row['Course']}<br>{row['Time']}",
            textposition='inside',
            hovertemplate=f"<b>{row['Course']}</b><br>" +
                         f"Day: {row['Day']}<br>" +
                         f"Time: {row['Time']}<br>" +
                         f"Mode: {row['Mode']}<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title="Your Weekly Class Schedule",
        xaxis=dict(
            title="Time of Day",
            tickmode='array',
            tickvals=[9, 12, 13, 16, 17, 20],
            ticktext=['9:00 AM', '12:00 PM', '1:00 PM', '4:00 PM', '5:00 PM', '8:00 PM'],
            range=[8, 21]
        ),
        yaxis=dict(
            title="",
            categoryorder='array',
            categoryarray=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        ),
        barmode='stack',
        height=400,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show summary by time slot
    st.markdown("#### 📊 Schedule Summary")
    col1, col2, col3 = st.columns(3)
    
    morning_count = len(calendar_df[calendar_df['Slot'] == 'Morning']['Course'].unique())
    afternoon_count = len(calendar_df[calendar_df['Slot'] == 'Afternoon']['Course'].unique())
    evening_count = len(calendar_df[calendar_df['Slot'] == 'Evening']['Course'].unique())
    
    with col1:
        st.metric("🌅 Morning Classes", morning_count, help="9:00 AM - 12:20 PM")
    with col2:
        st.metric("☀️ Afternoon Classes", afternoon_count, help="1:00 PM - 4:20 PM")
    with col3:
        st.metric("🌙 Evening Classes", evening_count, help="5:00 PM - 8:20 PM")


def render_grid_calendar(enrolled_courses, courses_df):
    """Render grid-style calendar view"""
    
    st.markdown("### 🗓️ Grid View")
    
    if not enrolled_courses:
        return
    
    # Generate calendar data
    calendar_df = generate_week_calendar(enrolled_courses, courses_df)
    
    if calendar_df.empty:
        return
    
    # Create grid
    time_slots_order = ['Morning', 'Afternoon', 'Evening']
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Create HTML table
    html = """
    <style>
    .calendar-grid {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .calendar-grid th {
        background: #1e40af;
        color: white;
        padding: 0.75rem;
        text-align: center;
        font-weight: 600;
    }
    .calendar-grid td {
        border: 1px solid #e5e7eb;
        padding: 0.5rem;
        min-height: 80px;
        vertical-align: top;
    }
    .calendar-grid .time-slot {
        background: #f3f4f6;
        font-weight: 600;
        text-align: center;
    }
    .course-pill {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        font-size: 0.85rem;
        font-weight: 500;
        display: block;
    }
    .course-pill.audit {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
    }
    </style>
    <table class="calendar-grid">
    <thead>
        <tr>
            <th>Time</th>
    """
    
    for day in days_order:
        html += f"<th>{day}</th>"
    html += "</tr></thead><tbody>"
    
    # Fill grid
    for slot in time_slots_order:
        html += "<tr>"
        
        # Time slot label
        slot_times = {
            'Morning': '9:00 AM<br>12:20 PM',
            'Afternoon': '1:00 PM<br>4:20 PM',
            'Evening': '5:00 PM<br>8:20 PM'
        }
        html += f'<td class="time-slot">{slot_times[slot]}</td>'
        
        # Each day
        for day in days_order:
            html += "<td>"
            # Find courses for this day and slot
            courses_here = calendar_df[(calendar_df['Day'] == day) & (calendar_df['Slot'] == slot)]
            for _, course in courses_here.iterrows():
                pill_class = "course-pill audit" if course['Mode'].lower() == 'audit' else "course-pill"
                html += f'<div class="{pill_class}">{course["Course"]}</div>'
            html += "</td>"
        
        html += "</tr>"
    
    html += "</tbody></table>"
    
    st.markdown(html, unsafe_allow_html=True)


def render_timeline_view(enrolled_courses, courses_df):
    """Render module timeline view"""
    
    st.markdown("### 📆 Module Timeline")
    
    if not enrolled_courses:
        st.info("Enroll in courses to see your module timeline!")
        return
    
    # Get current date and generate module schedule
    start_date = datetime.now()
    
    # Group courses by time slot
    course_details = []
    for enrolled_id in enrolled_courses:
        if ':' in str(enrolled_id):
            course_id, mode = str(enrolled_id).split(':')
        else:
            course_id = str(enrolled_id)
            mode = 'enroll'
        
        course_row = courses_df[courses_df['course_id'] == course_id]
        if not course_row.empty:
            course = course_row.iloc[0]
            course_details.append({
                'name': course['course_name'],
                'credits': course.get('credits', 3),
                'mode': mode,
                'time': course.get('class_time', 'TBD')
            })
    
    if not course_details:
        return
    
    # Create timeline
    timeline_data = []
    current_date = start_date
    
    # Assume 3-week modules
    for i, course in enumerate(course_details[:4]):  # Show first 4 courses
        module_num = (i // 3) + 1
        end_date = current_date + timedelta(weeks=3)
        
        timeline_data.append({
            'Module': f"Module {module_num}",
            'Course': course['name'],
            'Start': current_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d'),
            'Credits': course['credits']
        })
        
        if (i + 1) % 3 == 0:
            current_date = end_date
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Create Gantt chart
    fig = px.timeline(
        timeline_df,
        x_start='Start',
        x_end='End',
        y='Module',
        color='Course',
        hover_data=['Credits'],
        title="Your Course Timeline (Next 12 Weeks)"
    )
    
    fig.update_layout(
        height=300,
        showlegend=True,
        xaxis_title="Timeline",
        yaxis_title=""
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_print_friendly_schedule(enrolled_courses, courses_df):
    """Render print-friendly schedule view"""
    html_content = generate_print_friendly_html(enrolled_courses, courses_df)
    
    # Display in expandable section
    with st.expander("Print Preview", expanded=True):
        components.html(html_content, height=800, scrolling=True)
        st.markdown("""
        **To Print:**
        1. Click anywhere in the preview above
        2. Use Ctrl+P (Windows) or Cmd+P (Mac)
        3. Or right-click and select 'Print'
        """)


def render_full_calendar(student_id, courses_df):
    """Render complete calendar interface"""
    
    # Get enrolled courses
    enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
    
    # Add export options at the top
    if enrolled_courses:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col2:
            ical_data = generate_ical_export(enrolled_courses, courses_df)
            st.download_button(
                label="Export to Calendar",
                data=ical_data,
                file_name="my_schedule.ics",
                mime="text/calendar"
            )
        with col3:
            if st.button("Print View"):
                render_print_friendly_schedule(enrolled_courses, courses_df)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Weekly Calendar", "Grid View", "Timeline"])
    
    with tab1:
        render_calendar_view(enrolled_courses, courses_df)
    
    with tab2:
        render_grid_calendar(enrolled_courses, courses_df)
    
    with tab3:
        render_timeline_view(enrolled_courses, courses_df)
