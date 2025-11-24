import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# 1. FLASK SETUP
app = Flask(__name__)
app.secret_key = 'csci341_assignment3_secret'

# 2. DATABASE CONNECTION
# Use environment variable or default to the provided Neon DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'POSTGRES_URL', 
    "postgresql://neondb_owner:npg_YAa12uXvpOPd@ep-wandering-forest-ahwmlbmz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 3. DATABASE MODELS (ORM)

class User(db.Model):
    __tablename__ = 'USER' 
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    given_name = db.Column(db.String)
    surname = db.Column(db.String)
    city = db.Column(db.String)
    phone_number = db.Column(db.String)
    profile_description = db.Column(db.String)
    password = db.Column(db.String)

class Caregiver(db.Model):
    __tablename__ = 'caregiver'
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'), primary_key=True)
    photo = db.Column(db.String)
    gender = db.Column(db.String)
    caregiving_type = db.Column(db.String)
    hourly_rate = db.Column(db.Float)

class Member(db.Model):
    __tablename__ = 'member'
    member_user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'), primary_key=True)
    house_rules = db.Column(db.String)
    dependent_description = db.Column(db.String)

class Job(db.Model):
    __tablename__ = 'job'
    job_id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'))
    required_caregiving_type = db.Column(db.String)
    other_requirements = db.Column(db.String)
    date_posted = db.Column(db.Date)

class Address(db.Model):
    __tablename__ = 'address'
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'), primary_key=True)
    house_number = db.Column(db.String)
    street = db.Column(db.String)
    town = db.Column(db.String)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    appointment_id = db.Column(db.Integer, primary_key=True)
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'))
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.Time)
    work_hours = db.Column(db.Integer)
    status = db.Column(db.String)

class JobApplication(db.Model):
    __tablename__ = 'job_application'
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), primary_key=True)
    date_applied = db.Column(db.Date)

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
        users = db.session.execute(query).fetchall()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Database Error: {e}", "danger")
        return render_template('users.html', users=[])

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        # Manually delete dependencies first
        db.session.execute(text('DELETE FROM caregiver WHERE caregiver_user_id = :uid'), {'uid': user_id})
        db.session.execute(text('DELETE FROM member WHERE member_user_id = :uid'), {'uid': user_id})
        db.session.execute(text('DELETE FROM job WHERE member_user_id = :uid'), {'uid': user_id}) 
        db.session.execute(text('DELETE FROM "USER" WHERE user_id = :uid'), {'uid': user_id})
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
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
            db.session.add(new_user)
            db.session.flush()

            new_caregiver = Caregiver(
                caregiver_user_id=new_user.user_id,
                photo=request.form['photo'],
                gender=request.form['gender'],
                caregiving_type=request.form['caregiving_type'],
                hourly_rate=request.form['hourly_rate']
            )
            db.session.add(new_caregiver)
            db.session.commit()
            flash('Caregiver added successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('caregiver_form.html', action="Add")

@app.route('/caregiver/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_caregiver(user_id):
    user = db.session.get(User, user_id)
    caregiver = db.session.get(Caregiver, user_id)
    
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
            
            db.session.commit()
            flash('Caregiver updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
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
            db.session.add(new_user)
            db.session.flush()

            new_member = Member(
                member_user_id=new_user.user_id,
                house_rules=request.form['house_rules'],
                dependent_description=request.form['dependent_description']
            )
            db.session.add(new_member)
            db.session.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('member_form.html', action="Add")

@app.route('/member/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_member(user_id):
    user = db.session.get(User, user_id)
    member = db.session.get(Member, user_id)
    
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
            
            db.session.commit()
            flash('Member updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f"Update failed: {e}", "danger")

    return render_template('member_form.html', action="Edit", user=user, member=member)

# --- ADDRESS MANAGEMENT ---
@app.route('/address/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_address(user_id):
    address = db.session.get(Address, user_id)
    
    if request.method == 'POST':
        try:
            if not address:
                address = Address(member_user_id=user_id)
                db.session.add(address)
            
            address.house_number = request.form['house_number']
            address.street = request.form['street']
            address.town = request.form['town']
            
            db.session.commit()
            flash('Address updated!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
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
            db.session.add(new_job)
            db.session.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('list_jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('job_form.html', action="Add")

@app.route('/job/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        job = db.session.get(Job, job_id)
        if job:
            db.session.delete(job)
            db.session.commit()
            flash('Job deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting job: {e}", "danger")
    return redirect(url_for('list_jobs'))

# --- APPOINTMENT MANAGEMENT ---
@app.route('/appointments')
def list_appointments():
    try:
        appointments = db.session.query(Appointment).all()
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
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment created!', 'success')
            return redirect(url_for('list_appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('appointment_form.html')

@app.route('/appointment/status/<int:id>', methods=['POST'])
def update_appointment_status(id):
    try:
        appt = db.session.get(Appointment, id)
        if appt:
            appt.status = request.form['status']
            db.session.commit()
            flash('Status updated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_appointments'))

@app.route('/appointment/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    try:
        appt = db.session.get(Appointment, id)
        if appt:
            db.session.delete(appt)
            db.session.commit()
            flash('Appointment deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_appointments'))

# --- JOB APPLICATION MANAGEMENT ---
@app.route('/applications')
def list_applications():
    try:
        applications = db.session.query(JobApplication).all()
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
            db.session.add(new_app)
            db.session.commit()
            flash('Application submitted!', 'success')
            return redirect(url_for('list_applications'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('application_form.html')

@app.route('/application/delete/<int:caregiver_id>/<int:job_id>', methods=['POST'])
def delete_application(caregiver_id, job_id):
    try:
        app = db.session.get(JobApplication, (caregiver_id, job_id))
        if app:
            db.session.delete(app)
            db.session.commit()
            flash('Application deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('list_applications'))

if __name__ == '__main__':
    app.run(debug=True)