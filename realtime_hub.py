"""
Real-Time Hub Component with Clock and Course Tracking
"""
import streamlit as st
from datetime import datetime, timedelta
import time


def render_realtime_clock():
    """Render real-time clock with timezone"""
    
    # Get current time
    now = datetime.now()
    
    # Format time components
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%A, %B %d, %Y")
    
    # Determine time of day
    hour = now.hour
    if 5 <= hour < 12:
        time_of_day = "Morning"
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        time_of_day = "Afternoon"
        greeting = "Good Afternoon"
    elif 17 <= hour < 21:
        time_of_day = "Evening"
        greeting = "Good Evening"
    else:
        time_of_day = "Night"
        greeting = "Good Night"
    
    # Render clock
    st.markdown(f"""
    <div style="background: #1a1a1a; 
                padding: 1.5rem; border-radius: 8px; text-align: center; 
                color: white; border: 1px solid #2a2a2a;">
        <div style="font-size: 0.9rem; color: #888888; margin-bottom: 0.5rem;">
            {greeting}
        </div>
        <div style="font-size: 3rem; font-weight: 700; letter-spacing: 2px; margin: 0.5rem 0; color: #2563eb;">
            {current_time}
        </div>
        <div style="font-size: 1rem; color: #e0e0e0;">
            {current_date}
        </div>
        <div style="font-size: 0.85rem; color: #888888; margin-top: 0.5rem;">
            {time_of_day} Session
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return time_of_day, now


def get_current_class_slot(current_time):
    """Determine which class slot is currently active"""
    
    hour = current_time.hour
    minute = current_time.minute
    current_minutes = hour * 60 + minute
    
    # Define time slots in minutes from midnight
    slots = {
        'Morning': (9 * 60, 12 * 60 + 20),        # 9:00 - 12:20
        'Afternoon': (13 * 60, 16 * 60 + 20),     # 13:00 - 16:20
        'Evening': (17 * 60, 20 * 60 + 20)        # 17:00 - 20:20
    }
    
    for slot_name, (start, end) in slots.items():
        if start <= current_minutes <= end:
            # Calculate time remaining
            minutes_left = end - current_minutes
            return slot_name, minutes_left, True
    
    # Not in a class slot - find next one
    for slot_name, (start, end) in slots.items():
        if current_minutes < start:
            minutes_until = start - current_minutes
            return slot_name, minutes_until, False
    
    # After all slots - next class is tomorrow morning
    return 'Morning', None, False


def render_active_classes(student_id, courses_df):
    """Show currently active classes"""
    
    enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
    
    if not enrolled_courses:
        st.info("No enrolled courses. Visit Smart Path Planner to enroll!")
        return
    
    current_time = datetime.now()
    current_slot, time_info, is_active = get_current_class_slot(current_time)
    
    # Map slot names to class times
    slot_to_time = {
        'Morning': '9:00 AM - 12:20 PM',
        'Afternoon': '1:00 PM - 4:20 PM',
        'Evening': '5:00 PM - 8:20 PM'
    }
    
    current_class_time = slot_to_time.get(current_slot, '')
    
    # Find courses in current slot
    active_courses = []
    for enrolled_id in enrolled_courses:
        if ':' in str(enrolled_id):
            course_id, mode = str(enrolled_id).split(':')
        else:
            course_id = str(enrolled_id)
            mode = 'enroll'
        
        course_row = courses_df[courses_df['course_id'] == course_id]
        if not course_row.empty:
            course = course_row.iloc[0]
            if course.get('class_time', '') == current_class_time:
                active_courses.append({
                    'name': course['course_name'],
                    'id': course['course_id'],
                    'mode': mode
                })
    
    # Display status
    st.markdown("### Current Class Status")
    
    if is_active and active_courses:
        # Class is happening now
        hours = time_info // 60
        minutes = time_info % 60
        
        st.success(f"LIVE NOW: {current_slot} Session")
        st.info(f"Time Remaining: {hours}h {minutes}m")
        
        st.markdown("**Your Active Classes:**")
        for course in active_courses:
            mode_badge = "ENROLLED" if course['mode'] == 'enroll' else "AUDIT"
            st.markdown(f"""
            <div style="background: #1a1a1a; 
                        color: white; padding: 1rem; border-radius: 8px; 
                        margin: 0.5rem 0; border: 1px solid #16a34a;">
                <strong style="font-size: 1.1rem;">{course['name']}</strong><br>
                <span style="font-size: 0.85rem; color: #888888;">{course['id']} • {mode_badge}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Attendance reminder
        st.warning("Remember: 3 absences = Automatic fail")
        
    elif time_info is not None:
        # Upcoming class
        hours = time_info // 60
        minutes = time_info % 60
        
        st.info(f"Next Session: {current_slot}")
        st.write(f"Starts in: **{hours}h {minutes}m**")
        
        # Show courses for next slot
        upcoming_courses = []
        for enrolled_id in enrolled_courses:
            if ':' in str(enrolled_id):
                course_id, _ = str(enrolled_id).split(':')
            else:
                course_id = str(enrolled_id)
            
            course_row = courses_df[courses_df['course_id'] == course_id]
            if not course_row.empty:
                course = course_row.iloc[0]
                if course.get('class_time', '') == current_class_time:
                    upcoming_courses.append(course['course_name'])
        
        if upcoming_courses:
            st.markdown("**Prepare for:**")
            for course in upcoming_courses:
                st.write(f"- {course}")
    else:
        st.info("No more classes today. Rest well")


def render_today_schedule(student_id, courses_df):
    """Render today's full schedule"""
    
    st.markdown("### Today's Schedule")
    
    enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
    
    if not enrolled_courses:
        st.info("No classes scheduled for today.")
        return
    
    # Get all enrolled courses with times
    schedule = {
        '9:00 AM - 12:20 PM': [],
        '1:00 PM - 4:20 PM': [],
        '5:00 PM - 8:20 PM': []
    }
    
    for enrolled_id in enrolled_courses:
        if ':' in str(enrolled_id):
            course_id, mode = str(enrolled_id).split(':')
        else:
            course_id = str(enrolled_id)
            mode = 'enroll'
        
        course_row = courses_df[courses_df['course_id'] == course_id]
        if not course_row.empty:
            course = course_row.iloc[0]
            class_time = course.get('class_time', 'TBD')
            if class_time in schedule:
                schedule[class_time].append({
                    'name': course['course_name'],
                    'id': course['course_id'],
                    'mode': mode
                })
    
    # Display schedule
    current_time = datetime.now()
    current_slot, _, is_active = get_current_class_slot(current_time)
    
    slot_names = {
        '9:00 AM - 12:20 PM': 'Morning',
        '1:00 PM - 4:20 PM': 'Afternoon',
        '5:00 PM - 8:20 PM': 'Evening'
    }
    
    for time_slot, courses in schedule.items():
        slot_name = slot_names.get(time_slot, '')
        is_current = (slot_name == current_slot and is_active)
        
        # Styling based on status
        if is_current:
            bg_color = "#16a34a"
            status = "LIVE NOW"
        else:
            bg_color = "#2a2a2a"
            status = ""
        
        st.markdown(f"""
        <div style="background: {bg_color}; color: white; padding: 0.5rem 1rem; 
                    border-radius: 8px 8px 0 0; font-weight: 600; margin-top: 1rem;">
            {time_slot} {status}
        </div>
        """, unsafe_allow_html=True)
        
        if courses:
            for course in courses:
                mode_text = "ENROLLED" if course['mode'] == 'enroll' else "AUDIT"
                st.markdown(f"""
                <div style="background: #1a1a1a; border: 1px solid #2a2a2a; 
                            border-top: none; padding: 0.75rem 1rem; border-radius: 0 0 8px 8px;">
                    <strong style="color: #ffffff;">{course['name']}</strong><br>
                    <span style="font-size: 0.85rem; color: #888888;">
                        {course['id']} • {mode_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #1a1a1a; border: 1px solid #2a2a2a; border-top: none; 
                        padding: 0.75rem 1rem; border-radius: 0 0 8px 8px; color: #888888;">
                No classes scheduled
            </div>
            """, unsafe_allow_html=True)


def render_realtime_hub(student_id, courses_df):
    """Complete real-time hub with clock and course tracking"""
    
    st.markdown('<div class="section-header">Real-Time Hub</div>', unsafe_allow_html=True)
    
    # Two columns: Clock and Status
    col1, col2 = st.columns([1, 1])
    
    with col1:
        time_of_day, current_time = render_realtime_clock()
        
        # Quick stats
        st.markdown("#### Quick Stats")
        enrolled_count = len(st.session_state.enrolled_courses.get(student_id, []))
        completed_count = len(st.session_state.completed_courses.get(student_id, []))
        
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("Enrolled", enrolled_count)
        with stats_col2:
            st.metric("Completed", completed_count)
    
    with col2:
        render_active_classes(student_id, courses_df)
    
    # Full today's schedule
    st.markdown("---")
    render_today_schedule(student_id, courses_df)
    
    # Auto-refresh suggestion
    st.markdown("""
    <div style="background: #1a1a1a; padding: 0.5rem; border-radius: 6px; 
                text-align: center; font-size: 0.85rem; color: #888888; margin-top: 1rem; border: 1px solid #2a2a2a;">
        Tip: Refresh the page to update the real-time status
    </div>
    """, unsafe_allow_html=True)
