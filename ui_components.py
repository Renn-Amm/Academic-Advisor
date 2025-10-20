"""
UI Components for improved Smart Planner and Course Catalog
"""
import streamlit as st
import pandas as pd
from datetime import datetime


def render_enhanced_smart_planner(ai_model, student_id, student_data):
    """Render smart planner like course catalog - grid view"""
    st.markdown('<div class="section-header">Smart Path Planner</div>', unsafe_allow_html=True)
    
    major = student_data.get('major', 'Computer Science')
    career_goal = student_data.get('career_goal', '')
    experience_level = student_data.get('experience_level', 'Beginner')
    program = student_data.get('program', "Bachelor's Degree")
    
    st.subheader(f"Personalized Academic Plan for {major}")
    st.write("Your courses are organized by modules. Each module runs for 3 weeks.")
    
    # Get enrolled and completed
    enrolled = st.session_state.enrolled_courses.get(student_id, [])
    completed = st.session_state.completed_courses.get(student_id, [])
    
    # Generate schedule using enhanced advisor
    modules = ai_model.enhanced_advisor.generate_smart_schedule(
        student_data,
        enrolled_courses=enrolled,
        completed_courses=completed,
        limit_modules=4
    )
    
    if not modules:
        st.info("No courses available for planning. Please check the course catalog.")
        return
    
    # Handle course details modal ONCE at top level
    if 'show_course_details' in st.session_state and st.session_state.show_course_details:
        if 'selected_course' in st.session_state:
            @st.dialog("Course Details", width="large")
            def show_course_modal():
                course = st.session_state.selected_course
                course_modal_id = course.get('course_id', 'unknown')
                
                # Header with close button
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {course.get('course_name', 'N/A')}")
                    st.caption(f"**Course ID:** {course_modal_id}")
                with col2:
                    if st.button("Close", key=f"close_modal_{course_modal_id}", use_container_width=True):
                        st.session_state.show_course_details = False
                        st.rerun()
                
                st.divider()
                
                # Info grid - showing difficulty, credits, duration (3 weeks)
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    difficulty = course.get('estimated_difficulty', 'Intermediate')
                    st.metric("Difficulty", difficulty)
                with info_col2:
                    credits = course.get('credits', 4)
                    st.metric("Credits", credits)
                with info_col3:
                    st.metric("Duration", "3 weeks")  # Fixed: Always 3 weeks per module
                
                st.write("")
                
                # Skills section with badges - get from actual course data
                course_id = course.get('course_id')
                courses_df = ai_model.enhanced_advisor.courses_df
                course_row = courses_df[courses_df['course_id'] == course_id]
                
                if not course_row.empty:
                    actual_skills = course_row.iloc[0].get('skills_covered_str', '')
                    if actual_skills and str(actual_skills) != 'nan':
                        st.markdown("**Skills You'll Learn:**")
                        skills_list = [s.strip() for s in str(actual_skills).split(',') if s.strip()]
                        if skills_list:
                            skills_html = ' '.join([f"<span style='background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.6rem; border-radius: 5px; font-size: 0.85rem; margin: 0.2rem; display: inline-block;'>{skill}</span>" for skill in skills_list[:8]])
                            st.markdown(skills_html, unsafe_allow_html=True)
                            st.write("")
                
                # Description
                st.markdown("**Course Description:**")
                description = course.get('course_description', 'No description available')
                st.info(description)
                
                # Category and program
                st.write(f"**Program:** {course.get('category', 'N/A')}")
                st.write(f"**Schedule:** {course.get('class_time', 'TBD')}")
                st.write(f"**Course Type:** {course.get('course_type', 'secondary').upper()}")
                
                st.divider()
                
                # Lecturer section
                if course_id:
                    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course_id)
                    if lecturer:
                        st.markdown("**Instructor Information:**")
                        lect_col1, lect_col2 = st.columns([1, 3])
                        with lect_col1:
                            st.markdown(f"<div style='background: #f0f0f0; padding: 1rem; border-radius: 8px; text-align: center;'><div style='font-size: 2rem; font-weight: bold; color: #666;'>i</div><div style='font-size: 0.75rem; color: #666;'>Instructor</div></div>", unsafe_allow_html=True)
                        with lect_col2:
                            st.markdown(f"**{lecturer['name']}**")
                            st.write(f"{lecturer['job_title']}")
                            st.write(f"Email: {lecturer.get('email', 'N/A')}")
            
            # Call the modal
            show_course_modal()
    
    # Display modules in tabs for easy navigation
    module_tabs = st.tabs([f"Module {i+1}" for i in range(min(len(modules), 3))] + ["Upcoming"])
    
    # Display each module in its tab
    for idx, module in enumerate(modules[:3]):
        with module_tabs[idx]:
            render_module_as_catalog(module, idx + 1, ai_model, student_id, enrolled)
    
    # Coming soon tab
    with module_tabs[-1]:
        st.markdown("### Future Modules")
        st.info("Advanced and specialization courses will be added here as you progress through your program.")
        for idx in range(3, min(6, len(modules) + 2)):
            st.markdown(f"**Module {idx + 1}** - Available after completing Module {idx}")


def render_module_as_catalog(module, module_num, ai_model, student_id, enrolled_courses):
    """Render module courses in grid layout like course catalog"""
    # Module header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h3 style="margin: 0; color: white;">Module {module_num}</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{module['start_date'].strftime('%b %d')} - {module['end_date'].strftime('%b %d, %Y')} • {len(module['courses'])} Courses • 3 Weeks</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"**{module['description']}**")
    st.write("")
    
    # Modal is now handled at top level in render_enhanced_smart_planner
    
    # Display courses in grid (3 columns)
    num_courses = len(module['courses'])
    cols_per_row = 3
    
    for row_start in range(0, num_courses, cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            course_idx = row_start + col_idx
            if course_idx < num_courses:
                course = module['courses'][course_idx]
                with cols[col_idx]:
                    render_course_card_catalog_style(course, module_num, ai_model, student_id, enrolled_courses, course_idx)

def render_course_card_catalog_style(course, module_num, ai_model, student_id, enrolled_courses, unique_idx=0):
    """Render individual course card like course catalog"""
    # Convert course to dict if it's a Series
    if hasattr(course, 'to_dict'):
        course = course.to_dict()
    elif not isinstance(course, dict):
        course = dict(course)
    
    course_id = course['course_id']
    course_type = course.get('course_type', 'secondary')
    # Use class_time for consistency with detail modal
    time_slot = course.get('class_time', course.get('time_slot', 'TBD'))
    
    # Determine module access level
    # Module 1-2: Can enroll
    # Module 3: View only (no enrollment)
    # Module 4+: Coming soon
    is_current_module = (module_num <= 2)  # Allow enrollment in modules 1 and 2
    is_viewable_module = (module_num == 3)  # Module 3 is viewable but no enrollment
    
    # Check enrollment status (handle both old and new format)
    enrolled_courses = enrolled_courses if isinstance(enrolled_courses, list) else []
    # Check if enrolled in any mode and what mode
    is_enrolled = False
    enrollment_mode = None
    for e in enrolled_courses:
        if course_id in str(e):
            is_enrolled = True
            if ':' in str(e):
                # Extract mode from course_id:mode format
                enrollment_mode = str(e).split(':')[1]
            break
    
    # If enrolled in audit mode, change the displayed course type to audit
    if is_enrolled and enrollment_mode == 'audit':
        course_type = 'audit'
    
    # Type badge color
    type_colors = {
        'mandatory': '#e74c3c',
        'secondary': '#3498db',
        'audit': '#95a5a6'
    }
    type_color = type_colors.get(course_type, '#95a5a6')
    
    # Get skills for display
    skills = course.get('skills_covered_str', '')
    if skills:
        skills_display = f"<p style='color: #3b82f6; font-size: 0.75rem; margin: 0.3rem 0;'><strong>Skills:</strong> {skills[:50]}{'...' if len(skills) > 50 else ''}</p>"
    else:
        skills_display = ""
    
    # Card
    st.markdown(f"""
    <div style="background: white; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: 100%; border-top: 4px solid {type_color};">
        <div style="background: {type_color}; color: white; padding: 0.3rem 0.6rem; border-radius: 5px; display: inline-block; font-size: 0.75rem; font-weight: bold; margin-bottom: 0.5rem;">
            {course_type.upper()}
        </div>
        <h4 style="margin: 0.5rem 0; color: #2c3e50;">{course['course_name']}</h4>
        <p style="color: #7f8c8d; font-size: 0.85rem; margin: 0.3rem 0;">{course_id}</p>
        {skills_display}
        <p style="color: #5a6c7d; font-size: 0.85rem; margin: 0.5rem 0;">
            Time: {time_slot}<br/>
            Duration: 3 weeks<br/>
            Level: {course.get('estimated_difficulty', 'Intermediate')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lecturer info
    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course_id)
    if lecturer:
        st.caption(f"Instructor: {lecturer['name']}")
    
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Details", key=f"mod{module_num}_{course_id}_details_{unique_idx}", use_container_width=True):
            st.session_state.selected_course = course  # Already converted to dict at function start
            st.session_state.show_course_details = True
    
    with col2:
        if is_current_module:
            # Modules 1-2: Allow enrollment
            if is_enrolled:
                st.success("Enrolled")
            else:
                # For secondary/audit courses, show audit option
                if course_type in ['secondary', 'audit']:
                    enroll_type = st.selectbox(
                        "Mode",
                        ["Enroll", "Audit"],
                        key=f"mod{module_num}_{course_id}_mode_{unique_idx}",
                        label_visibility="collapsed"
                    )
                    if st.button("Confirm", key=f"mod{module_num}_{course_id}_enroll_{unique_idx}", use_container_width=True, type="primary"):
                        if student_id not in st.session_state.enrolled_courses:
                            st.session_state.enrolled_courses[student_id] = []
                        
                        # Check if already enrolled (prevent duplicates)
                        enrolled_list = st.session_state.enrolled_courses[student_id]
                        already_enrolled = any(course_id in str(e) for e in enrolled_list)
                        
                        if not already_enrolled:
                            # Store with mode
                            enroll_data = f"{course_id}:{enroll_type.lower()}"
                            st.session_state.enrolled_courses[student_id].append(enroll_data)
                            st.success(f"Enrolled in {enroll_type} mode!")
                            st.rerun()
                        else:
                            st.warning("Already enrolled in this course!")
                else:
                    # Mandatory courses - direct enrollment
                    if st.button("Enroll", key=f"mod{module_num}_{course_id}_enroll_{unique_idx}", use_container_width=True, type="primary"):
                        if student_id not in st.session_state.enrolled_courses:
                            st.session_state.enrolled_courses[student_id] = []
                        
                        # Check if already enrolled (prevent duplicates)
                        enrolled_list = st.session_state.enrolled_courses[student_id]
                        already_enrolled = any(course_id in str(e) for e in enrolled_list)
                        
                        if not already_enrolled:
                            # Check for time conflicts
                            courses_df = ai_model.enhanced_advisor.courses_df
                            current_course_time = courses_df[courses_df['course_id'] == course_id].iloc[0].get('class_time', '')
                            
                            has_conflict = False
                            conflict_course = None
                            for enrolled in enrolled_list:
                                enrolled_id = enrolled.split(':')[0]
                                enrolled_course_row = courses_df[courses_df['course_id'] == enrolled_id]
                                if not enrolled_course_row.empty:
                                    enrolled_time = enrolled_course_row.iloc[0].get('class_time', '')
                                    if enrolled_time and current_course_time and enrolled_time == current_course_time:
                                        has_conflict = True
                                        conflict_course = enrolled_course_row.iloc[0]['course_name']
                                        break
                            
                            if has_conflict:
                                st.error(f"TIME CONFLICT! This course conflicts with '{conflict_course}' ({current_course_time}). Please drop that course first.")
                            else:
                                st.session_state.enrolled_courses[student_id].append(f"{course_id}:enroll")
                                st.success("Enrolled successfully!")
                                st.rerun()
                        else:
                            st.warning("Already enrolled in this course!")
        elif is_viewable_module:
            # Module 3: View only, no enrollment
            st.info("View Only")
        else:
            # Module 4+: Coming soon
            st.warning("Coming Soon")

def render_module_card(module, module_num, ai_model, student_id):
    """Render a single module card with time slots"""
    with st.expander(
        f"**Module {module_num}** | "
        f"{module['start_date'].strftime('%b %d, %Y')} - {module['end_date'].strftime('%b %d, %Y')} | "
        f"{module['total_credits']} credits | "
        f"{len(module['courses'])} courses",
        expanded=(module_num == 1)
    ):
        st.write(f"**Description:** {module['description']}")
        st.write("**Schedule:** 3 hours and 20 minutes per class | Monday to Friday")
        st.write("**Attendance Policy:** Max 3 absences | Late arrival >10 min = absence | 3 absences = fail")
        
        st.markdown("### Courses")
        
        for idx, course in enumerate(module['courses']):
            render_course_in_module(course, idx, module_num, ai_model, student_id)


def render_course_in_module(course, idx, module_num, ai_model, student_id):
    """Render individual course in module with time slot and type changer"""
    course_id = course['course_id']
    # Use class_time for consistency with detail modal
    time_slot = course.get('class_time', course.get('time_slot', 'TBD'))
    
    # Create unique key for this course instance
    key_prefix = f"mod{module_num}_course{idx}_{course_id}"
    
    # Use a container for proper spacing
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #667eea; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h4 style="margin: 0 0 0.8rem 0; color: #2c3e50;">{course['course_name']}</h4>
        <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
            <strong>Course ID:</strong> {course_id} | <strong>Credits:</strong> {course.get('credits', 3)} | <strong>Type:</strong> {course.get('course_type', 'secondary').upper()}
        </div>
        <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
            <strong>Time:</strong> {time_slot} | <strong>Duration:</strong> 3 weeks
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Course type selector in separate row
    col_type, col_spacer = st.columns([2, 3])
    with col_type:
        current_type = course.get('course_type', 'secondary')
        type_options = ['mandatory', 'secondary', 'audit']
        type_labels = {
            'mandatory': 'Mandatory',
            'secondary': 'Secondary',
            'audit': 'Audit (Optional)'
        }
        
        selected_type = st.selectbox(
            "Take this course as:",
            type_options,
            index=type_options.index(current_type),
            format_func=lambda x: type_labels[x],
            key=f"{key_prefix}_type"
        )
        
        if selected_type != current_type:
            # Update course type in session state if needed
            if 'course_type_changes' not in st.session_state:
                st.session_state.course_type_changes = {}
            st.session_state.course_type_changes[course_id] = selected_type
    
    # Lecturer information
    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course_id)
    if lecturer:
        with st.expander("Instructor Details"):
            st.write(f"**Name:** {lecturer['name']}")
            st.write(f"**Title:** {lecturer['job_title']} at {lecturer['company']}")
            st.write(f"**Expertise:** {lecturer['expertise_areas']}")
            st.write(f"**Background:** {lecturer.get('background', 'N/A')}")
            st.write(f"**Contact:** {lecturer.get('email', 'N/A')}")
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("View Details", key=f"{key_prefix}_details", use_container_width=True):
            show_enhanced_course_details(course, ai_model)
    with btn_col2:
        if st.button("Enroll", key=f"{key_prefix}_enroll", use_container_width=True):
            enroll_course_enhanced(course, student_id, selected_type)
    with btn_col3:
        if st.button("Alternatives", key=f"{key_prefix}_alt", use_container_width=True):
            show_alternatives_enhanced(course, ai_model, student_id)
    
    st.divider()


def show_course_details_sidebar(course, ai_model):
    """Show course details in sidebar - clean and informative"""
    st.sidebar.markdown("### Course Details")
    st.sidebar.markdown(f"**{course['course_name']}**")
    st.sidebar.caption(f"Course ID: {course['course_id']}")
    st.sidebar.divider()
    
    st.sidebar.write(f"**Category:** {course['category']}")
    st.sidebar.write(f"**Difficulty:** {course.get('estimated_difficulty', 'Intermediate')}")
    st.sidebar.write(f"**Duration:** 3 weeks")
    st.sidebar.divider()
    
    st.sidebar.markdown("#### Description")
    st.sidebar.write(course['course_description'])
    st.sidebar.divider()
    
    # Lecturer
    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course['course_id'])
    if lecturer:
        st.sidebar.markdown("#### Instructor")
        st.sidebar.write(f"**{lecturer['name']}**")
        st.sidebar.write(f"{lecturer['job_title']}")
        st.sidebar.write(f"Company: {lecturer['company']}")
        st.sidebar.write(f"Email: {lecturer.get('email', 'N/A')}")
        st.sidebar.divider()
    
    # Skills
    st.sidebar.markdown("#### Skills You'll Learn")
    skills = course.get('skills_covered_str', 'Various skills')
    st.sidebar.write(skills)
    st.sidebar.divider()
    
    # Prerequisites
    st.sidebar.markdown("#### Prerequisites")
    prereqs = ai_model.enhanced_advisor._get_prerequisite_skills(course)
    if prereqs:
        for prereq in prereqs:
            st.sidebar.write(f"• {prereq}")
    else:
        st.sidebar.write("No specific prerequisites required")

def show_enhanced_course_details(course, ai_model):
    """Show enhanced course details with lecturer info"""
    st.sidebar.markdown("### Course Details")
    st.sidebar.write(f"**{course['course_name']}**")
    st.sidebar.write(f"**Course ID:** {course['course_id']}")
    st.sidebar.write(f"**Category:** {course['category']}")
    st.sidebar.write(f"**Difficulty:** {course.get('estimated_difficulty', 'Intermediate')}")
    st.sidebar.write("---")
    
    # Lecturer info
    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course['course_id'])
    if lecturer:
        st.sidebar.markdown("#### Instructor")
        st.sidebar.write(f"**{lecturer['name']}**")
        st.sidebar.write(f"{lecturer['job_title']}")
        st.sidebar.write(f"*{lecturer['company']}*")
        st.sidebar.write(f"**Expertise:** {lecturer['expertise_areas']}")
        st.sidebar.write("---")
    
    st.sidebar.write("**Description:**")
    st.sidebar.write(course['course_description'])
    st.sidebar.write("---")
    st.sidebar.write("**Skills Covered:**")
    st.sidebar.write(course.get('skills_covered_str', 'Various skills'))
    st.sidebar.write("---")
    st.sidebar.write("**Prerequisites to Prepare:**")
    # Get prerequisites from enhanced advisor
    prereqs = ai_model.enhanced_advisor._get_prerequisite_skills(course)
    if prereqs:
        for prereq in prereqs:
            st.sidebar.write(f"• {prereq}")
    else:
        st.sidebar.write("• No specific prerequisites")


def enroll_course_enhanced(course, student_id, course_type):
    """Enroll with selected course type and collision detection"""
    if student_id not in st.session_state.enrolled_courses:
        st.session_state.enrolled_courses[student_id] = []
    
    # Check if already enrolled
    if course['course_id'] in st.session_state.enrolled_courses[student_id]:
        st.warning(f"Already enrolled in {course['course_name']}")
        return
    
    # Check for timetable conflicts
    courses_df = st.session_state.ai_model.courses_df
    new_course_time = course.get('class_time', '')
    
    if new_course_time and new_course_time != 'TBD':
        # Get currently enrolled courses
        enrolled_course_ids = st.session_state.enrolled_courses[student_id]
        conflicting_courses = []
        
        for enrolled_id in enrolled_course_ids:
            # Parse course_id:mode format if present
            if ':' in str(enrolled_id):
                enrolled_id, _ = str(enrolled_id).split(':')
            
            enrolled_course_row = courses_df[courses_df['course_id'] == enrolled_id]
            if not enrolled_course_row.empty:
                enrolled_time = enrolled_course_row.iloc[0].get('class_time', '')
                if enrolled_time == new_course_time:
                    conflicting_courses.append({
                        'id': enrolled_id,
                        'name': enrolled_course_row.iloc[0]['course_name'],
                        'time': enrolled_time
                    })
        
        # If conflicts found, show error
        if conflicting_courses:
            st.error(f"⚠️ **TIMETABLE CONFLICT!**")
            st.error(f"**{course['course_name']}** ({new_course_time}) conflicts with:")
            for conflict in conflicting_courses:
                st.error(f"  • {conflict['name']} at {conflict['time']}")
            st.warning("🚫 Cannot enroll - courses have same time slot!")
            return
    
    # No conflicts - proceed with enrollment
    enrollment_id = f"{course['course_id']}:{course_type}"
    st.session_state.enrolled_courses[student_id].append(enrollment_id)
    
    type_label = {
        'mandatory': 'Mandatory',
        'secondary': 'Secondary',
        'audit': 'Audit'
    }[course_type]
    st.success(f"✅ Enrolled in {course['course_name']} as {type_label}!")
    
    if new_course_time and new_course_time != 'TBD':
        st.info(f"📅 Class Time: {new_course_time}")


def show_alternatives_enhanced(course, ai_model, student_id):
    """Show alternative courses"""
    st.sidebar.markdown("### Alternative Courses")
    st.sidebar.write(f"Alternatives to **{course['course_name']}**")
    
    alternatives = ai_model.suggest_alternative_courses(course, student_id)
    
    if not alternatives.empty:
        for _, alt in alternatives.iterrows():
            st.sidebar.write(f"**{alt['course_name']}** ({alt['course_id']})")
            st.sidebar.write(f"Credits: {alt['credits']} | Difficulty: {alt.get('estimated_difficulty', 'N/A')}")
            if st.sidebar.button(f"Switch to {alt['course_id']}", key=f"alt_{alt['course_id']}"):
                enroll_course_enhanced(alt.to_dict(), student_id, alt['course_type'])
            st.sidebar.write("---")
    else:
        st.sidebar.info("No alternatives available")


def render_enhanced_course_catalog(ai_model, student_data):
    """Enhanced course catalog - clean view for exploration"""
    st.markdown('<div class="section-header">Course Catalog</div>', unsafe_allow_html=True)
    
    major = student_data.get('major', 'Computer Science')
    student_id = st.session_state.current_user
    st.write(f"Browse all available courses. Enroll if in current module or view for future planning.")
    
    # Get current module courses
    enrolled = st.session_state.enrolled_courses.get(student_id, [])
    completed = st.session_state.completed_courses.get(student_id, [])
    modules = ai_model.enhanced_advisor.generate_smart_schedule(
        student_data,
        enrolled_courses=enrolled,
        completed_courses=completed,
        limit_modules=4
    )
    current_module_courses = []
    if modules and len(modules) > 0:
        current_module_courses = [c['course_id'] for c in modules[0]['courses']]
    
    # Get all unique programs from courses
    courses_df = ai_model.courses_df
    if courses_df is None or courses_df.empty:
        st.warning("No courses available in the catalog.")
        return
    
    # Get unique categories/programs
    all_programs = sorted(courses_df['category'].unique().tolist())
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        major_filter = st.selectbox("Program",  ["All"] + all_programs)
    with col2:
        difficulty_filter = st.selectbox("Difficulty", 
                                       ["All", "Beginner", "Intermediate", "Advanced"])
    with col3:
        search_query = st.text_input("Search", placeholder="Course name, skills...")
    
    # Apply filters
    filtered_courses = courses_df.copy()
    
    if major_filter != "All":
        # Use exact match since we're getting values from the data
        filtered_courses = filtered_courses[filtered_courses['category'] == major_filter]
    if difficulty_filter != "All":
        filtered_courses = filtered_courses[filtered_courses['estimated_difficulty'] == difficulty_filter]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_courses = filtered_courses[
            filtered_courses['course_name'].str.contains(search_lower, case=False, na=False) |
            filtered_courses['course_description'].str.contains(search_lower, case=False, na=False) |
            filtered_courses['skills_covered_str'].str.contains(search_lower, case=False, na=False)
        ]
    
    # Display courses
    st.write(f"**Found {len(filtered_courses)} courses**")
    
    if filtered_courses.empty:
        st.info("No courses match your filters. Try adjusting your search criteria.")
        return
    
    # Show course details modal if selected
    if 'show_course_details_catalog' in st.session_state and st.session_state.show_course_details_catalog:
        if 'selected_course' in st.session_state:
            @st.dialog("Course Details", width="large")
            def show_catalog_modal():
                course = st.session_state.selected_course
                
                # Header
                st.markdown(f"### {course.get('course_name', 'N/A')}")
                st.caption(f"**Course ID:** {course.get('course_id', 'N/A')}")
                
                if st.button("Close", key="close_catalog_details", use_container_width=False):
                    st.session_state.show_course_details_catalog = False
                    st.rerun()
                
                st.divider()
                
                # Info grid - Difficulty, Credits, Duration (3 weeks fixed)
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    difficulty = course.get('estimated_difficulty', 'Intermediate')
                    st.metric("Difficulty", difficulty)
                with info_col2:
                    credits = course.get('credits', 4)
                    st.metric("Credits", credits)
                with info_col3:
                    st.metric("Duration", "3 weeks")  # Fixed: Always 3 weeks per module
                
                st.write("")
                
                # Skills section with badges - get from actual course data
                course_id = course.get('course_id')
                courses_df = ai_model.enhanced_advisor.courses_df
                course_row = courses_df[courses_df['course_id'] == course_id]
                
                if not course_row.empty:
                    actual_skills = course_row.iloc[0].get('skills_covered_str', '')
                    if actual_skills and str(actual_skills) != 'nan':
                        st.markdown("**Skills You'll Learn:**")
                        skills_list = [s.strip() for s in str(actual_skills).split(',') if s.strip()]
                        if skills_list:
                            skills_html = ' '.join([f"<span style='background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.6rem; border-radius: 5px; font-size: 0.85rem; margin: 0.2rem; display: inline-block;'>{skill}</span>" for skill in skills_list[:8]])
                            st.markdown(skills_html, unsafe_allow_html=True)
                            st.write("")
                
                # Description
                st.markdown("**Course Description:**")
                description = course.get('course_description', 'No description available')
                st.info(description)
                
                # Category and program info
                st.write(f"**Program:** {course.get('category', 'N/A')}")
                st.write(f"**Schedule:** {course.get('class_time', 'TBD')}")
                st.write(f"**Course Type:** {course.get('course_type', 'secondary').upper()}")
                
                st.divider()
                
                # Lecturer
                course_id = course.get('course_id')
                if course_id:
                    lecturer = ai_model.enhanced_advisor.get_lecturer_details(course_id)
                    if lecturer:
                        st.markdown("**Instructor Information:**")
                        lect_col1, lect_col2 = st.columns([1, 3])
                        with lect_col1:
                            st.markdown(f"<div style='background: #f0f0f0; padding: 1rem; border-radius: 8px; text-align: center;'><div style='font-size: 2rem; font-weight: bold; color: #666;'>i</div><div style='font-size: 0.75rem; color: #666;'>Instructor</div></div>", unsafe_allow_html=True)
                        with lect_col2:
                            st.markdown(f"**{lecturer['name']}**")
                            st.write(f"{lecturer['job_title']}")
                            st.write(f"Email: {lecturer.get('email', 'N/A')}")
            
            # Call the modal
            show_catalog_modal()
    
    # Create responsive grid
    cols = st.columns(3)
    
    for idx, (_, course) in enumerate(filtered_courses.iterrows()):
        col = cols[idx % 3]
        
        with col:
            difficulty = course.get('estimated_difficulty', 'Intermediate')
            difficulty_color = {
                'Beginner': '#2ecc71',
                'Intermediate': '#f39c12',
                'Advanced': '#e74c3c'
            }.get(difficulty, '#95a5a6')
            
            # Card without credits display
            st.markdown(f"""
            <div style="background: white; padding: 1.2rem; border-radius: 10px; border-left: 5px solid #667eea; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem; min-height: 200px;">
                <h4 style="margin: 0 0 0.8rem 0; color: #2c3e50; font-size: 1.05rem;">{course['course_name']}</h4>
                <div style="color: #7f8c8d; font-size: 0.85rem; margin-bottom: 0.4rem;">
                    {course['course_id']}
                </div>
                <div style="color: #5a6c7d; font-size: 0.85rem; margin-bottom: 0.4rem;">
                    Duration: 3 weeks
                </div>
                <div style="color: {difficulty_color}; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem;">
                    Level: {difficulty}
                </div>
                <div style="color: #5a6c7d; font-size: 0.8rem; line-height: 1.3;">
                    {course.get('course_description', '')[:100]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Conditional buttons
            course_id = course['course_id']
            is_in_current_module = course_id in current_module_courses
            is_enrolled = course_id in enrolled
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("View Details", key=f"cat_det_{course_id}_{idx}", use_container_width=True):
                    st.session_state.selected_course = course.to_dict() if hasattr(course, 'to_dict') else dict(course)
                    st.session_state.show_course_details_catalog = True
            with btn_col2:
                if is_enrolled:
                    st.success("Enrolled")
                elif is_in_current_module:
                    # Current module - allow enrollment with time conflict check
                    if st.button("Enroll Now", key=f"cat_enr_{course_id}_{idx}", use_container_width=True, type="primary"):
                        if student_id not in st.session_state.enrolled_courses:
                            st.session_state.enrolled_courses[student_id] = []
                        
                        # Check for time conflicts
                        courses_df = ai_model.enhanced_advisor.courses_df
                        current_course_time = course.get('class_time', '')
                        
                        has_conflict = False
                        conflict_course = None
                        enrolled_list = st.session_state.enrolled_courses[student_id]
                        for enrolled_id in enrolled_list:
                            enrolled_course_row = courses_df[courses_df['course_id'] == enrolled_id]
                            if not enrolled_course_row.empty:
                                enrolled_time = enrolled_course_row.iloc[0].get('class_time', '')
                                if enrolled_time and current_course_time and enrolled_time == current_course_time:
                                    has_conflict = True
                                    conflict_course = enrolled_course_row.iloc[0]['course_name']
                                    break
                        
                        if has_conflict:
                            st.error(f"TIME CONFLICT! This course conflicts with '{conflict_course}' ({current_course_time}). Please drop that course first.")
                        else:
                            st.session_state.enrolled_courses[student_id].append(course_id)
                            st.success("Enrolled successfully!")
                            st.rerun()
                else:
                    # Future module - just viewing
                    st.info("Future")
