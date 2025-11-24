from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey

# 1. FLASK SETUP
app = Flask(__name__)
app.secret_key = 'csci341_assignment3_secret'

# 2. DATABASE CONNECTION
# CHANGE THIS TO YOUR ACTUAL DATABASE URL
DATABASE_URL = "postgresql://postgres:9@localhost:5432/dbass3"

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# 3. DATABASE MODELS (ORM)

class User(Base):
    __tablename__ = 'USER' 
    user_id = Column(Integer, primary_key=True)
    email = Column(String)
    given_name = Column(String)
    surname = Column(String)
    city = Column(String)
    phone_number = Column(String)
    profile_description = Column(String)
    password = Column(String)

class Caregiver(Base):
    __tablename__ = 'caregiver'
    caregiver_user_id = Column(Integer, ForeignKey('USER.user_id'), primary_key=True)
    photo = Column(String)
    gender = Column(String)
    caregiving_type = Column(String)
    hourly_rate = Column(Float)

class Member(Base):
    __tablename__ = 'member'
    member_user_id = Column(Integer, ForeignKey('USER.user_id'), primary_key=True)
    house_rules = Column(String)
    dependent_description = Column(String)

class Job(Base):
    __tablename__ = 'job'
    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey('USER.user_id'))
    required_caregiving_type = Column(String)
    other_requirements = Column(String)
    date_posted = Column(Date)

class Address(Base):
    __tablename__ = 'address'
    member_user_id = Column(Integer, ForeignKey('member.member_user_id'), primary_key=True)
    house_number = Column(String)
    street = Column(String)
    town = Column(String)

class Appointment(Base):
    __tablename__ = 'appointment'
    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey('caregiver.caregiver_user_id'))
    member_user_id = Column(Integer, ForeignKey('member.member_user_id'))
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Integer)
    status = Column(String)

class JobApplication(Base):
    __tablename__ = 'job_application'
    caregiver_user_id = Column(Integer, ForeignKey('caregiver.caregiver_user_id'), primary_key=True)
    job_id = Column(Integer, ForeignKey('job.job_id'), primary_key=True)
    date_applied = Column(Date)

# 4. WEB ROUTES (CRUD OPERATIONS)

@app.route('/')
def index():
    return render_template('index.html')

# --- USER MANAGEMENT ---
@app.route('/users')
def list_users():
    try:
        query = text("""
            SELECT u.*, 
                   CASE WHEN c.caregiver_user_id IS NOT NULL THEN 'Caregiver' ELSE 'Member/User' END as role
            FROM "USER" u
            LEFT JOIN caregiver c ON u.user_id = c.caregiver_user_id
            ORDER BY u.user_id
        """)
        users = db_session.execute(query).fetchall()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Database Error: {e}", "danger")
        return render_template('users.html', users=[])

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        # Manually delete dependencies first
        db_session.execute(text('DELETE FROM caregiver WHERE caregiver_user_id = :uid'), {'uid': user_id})
        db_session.execute(text('DELETE FROM member WHERE member_user_id = :uid'), {'uid': user_id})
        db_session.execute(text('DELETE FROM job WHERE member_user_id = :uid'), {'uid': user_id}) 
        db_session.execute(text('DELETE FROM "USER" WHERE user_id = :uid'), {'uid': user_id})
        db_session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    return redirect(url_for('list_users'))

# --- CAREGIVER (CREATE & UPDATE) ---
@app.route('/caregiver/add', methods=['GET', 'POST'])
def add_caregiver():
    if request.method == 'POST':
        try:
            new_user = User(
                user_id=request.form['user_id'],
                email=request.form['email'],
                given_name=request.form['given_name'],
                surname=request.form['surname'],
                city=request.form['city'],
                phone_number=request.form['phone_number'],
                profile_description=request.form['profile_description'],
                password=request.form['password']
            )
            db_session.add(new_user)
            db_session.flush()

            new_caregiver = Caregiver(
                caregiver_user_id=new_user.user_id,
                photo=request.form['photo'],
                gender=request.form['gender'],
                caregiving_type=request.form['caregiving_type'],
                hourly_rate=request.form['hourly_rate']
            )
            db_session.add(new_caregiver)
            db_session.commit()
            flash('Caregiver added successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('caregiver_form.html', action="Add")

@app.route('/caregiver/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_caregiver(user_id):
    user = db_session.query(User).get(user_id)
    caregiver = db_session.query(Caregiver).get(user_id)
    
    if not user or not caregiver:
        flash("Caregiver not found.", "danger")
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        try:
            user.email = request.form['email']
            user.given_name = request.form['given_name']
            user.surname = request.form['surname']
            user.city = request.form['city']
            user.phone_number = request.form['phone_number']
            
            caregiver.hourly_rate = request.form['hourly_rate']
            caregiver.caregiving_type = request.form['caregiving_type']
            
            db_session.commit()
            flash('Caregiver updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db_session.rollback()
            flash(f"Update failed: {e}", "danger")

    return render_template('caregiver_form.html', action="Edit", user=user, caregiver=caregiver)

# --- MEMBER (CREATE & UPDATE) ---
@app.route('/member/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        try:
            new_user = User(
                user_id=request.form['user_id'],
                email=request.form['email'],
                given_name=request.form['given_name'],
                surname=request.form['surname'],
                city=request.form['city'],
                phone_number=request.form['phone_number'],
                profile_description=request.form['profile_description'],
                password=request.form['password']
            )
            db_session.add(new_user)
            db_session.flush()

            new_member = Member(
                member_user_id=new_user.user_id,
                house_rules=request.form['house_rules'],
                dependent_description=request.form['dependent_description']
            )
            db_session.add(new_member)
            db_session.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('member_form.html', action="Add")

@app.route('/member/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_member(user_id):
    user = db_session.query(User).get(user_id)
    member = db_session.query(Member).get(user_id)
    
    if not user or not member:
        flash("Member not found.", "danger")
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        try:
            user.email = request.form['email']
            user.given_name = request.form['given_name']
            user.surname = request.form['surname']
            user.city = request.form['city']
            user.phone_number = request.form['phone_number']
            
            member.house_rules = request.form['house_rules']
            member.dependent_description = request.form['dependent_description']
            
            db_session.commit()
            flash('Member updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db_session.rollback()
            flash(f"Update failed: {e}", "danger")

    return render_template('member_form.html', action="Edit", user=user, member=member)

# --- ADDRESS MANAGEMENT ---
@app.route('/address/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_address(user_id):
    address = db_session.query(Address).get(user_id)
    
    if request.method == 'POST':
        try:
            if not address:
                address = Address(member_user_id=user_id)
                db_session.add(address)
            
            address.house_number = request.form['house_number']
            address.street = request.form['street']
            address.town = request.form['town']
            
            db_session.commit()
            flash('Address updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db_session.rollback()
            flash(f"Update failed: {e}", "danger")
            
    return render_template('address_form.html', address=address, user_id=user_id)

# --- JOB MANAGEMENT (CRUD) ---
@app.route('/jobs')
def list_jobs():
    try:
        jobs = Job.query.all()
        return render_template('jobs.html', jobs=jobs)
    except Exception as e:
        flash(f"Error loading jobs: {e}", "danger")
        return render_template('jobs.html', jobs=[])

@app.route('/job/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        try:
            new_job = Job(
                job_id=request.form['job_id'],
                member_user_id=request.form['member_user_id'],
                required_caregiving_type=request.form['required_caregiving_type'],
                other_requirements=request.form['other_requirements'],
                date_posted=request.form['date_posted']
            )
            db_session.add(new_job)
            db_session.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('list_jobs'))
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('job_form.html', action="Add")

@app.route('/job/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        job = Job.query.get(job_id)
        if job:
            db_session.delete(job)
            db_session.commit()
            flash('Job deleted.', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f"Error deleting job: {e}", "danger")
    return redirect(url_for('list_jobs'))

# --- APPOINTMENT MANAGEMENT ---
@app.route('/appointments')
def list_appointments():
    try:
        appointments = db_session.query(Appointment).all()
        return render_template('appointments.html', appointments=appointments)
    except Exception as e:
        flash(f"Error loading appointments: {e}", "danger")
        return render_template('appointments.html', appointments=[])

@app.route('/appointment/add', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        try:
            new_appt = Appointment(
                appointment_id=request.form['appointment_id'],
                caregiver_user_id=request.form['caregiver_user_id'],
                member_user_id=request.form['member_user_id'],
                appointment_date=request.form['appointment_date'],
                appointment_time=request.form['appointment_time'],
                work_hours=request.form['work_hours'],
                status='Pending'
            )
            db_session.add(new_appt)
            db_session.commit()
            flash('Appointment created!', 'success')
            return redirect(url_for('list_appointments'))
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('appointment_form.html')

@app.route('/appointment/status/<int:id>', methods=['POST'])
def update_appointment_status(id):
    try:
        appt = db_session.query(Appointment).get(id)
        if appt:
            appt.status = request.form['status']
            db_session.commit()
            flash('Status updated.', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_appointments'))

@app.route('/appointment/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    try:
        appt = db_session.query(Appointment).get(id)
        if appt:
            db_session.delete(appt)
            db_session.commit()
            flash('Appointment deleted.', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_appointments'))

# --- JOB APPLICATION MANAGEMENT ---
@app.route('/applications')
def list_applications():
    try:
        applications = db_session.query(JobApplication).all()
        return render_template('applications.html', applications=applications)
    except Exception as e:
        flash(f"Error loading applications: {e}", "danger")
        return render_template('applications.html', applications=[])

@app.route('/application/add', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        try:
            new_app = JobApplication(
                caregiver_user_id=request.form['caregiver_user_id'],
                job_id=request.form['job_id'],
                date_applied=request.form['date_applied']
            )
            db_session.add(new_app)
            db_session.commit()
            flash('Application submitted!', 'success')
            return redirect(url_for('list_applications'))
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('application_form.html')

@app.route('/application/delete/<int:caregiver_id>/<int:job_id>', methods=['POST'])
def delete_application(caregiver_id, job_id):
    try:
        app = db_session.query(JobApplication).get((caregiver_id, job_id))
        if app:
            db_session.delete(app)
            db_session.commit()
            flash('Application deleted.', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_applications'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)