"""
CSCI 341 - Assignment 3 - Part 2
Database Queries using SQLAlchemy

INSTALLATION REQUIRED:
pip install sqlalchemy psycopg2-binary

Replace the DATABASE_URL with your PostgreSQL credentials.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ==================== DATABASE CONNECTION ====================
# CHANGE THESE VALUES to match your PostgreSQL setup
DATABASE_URL = "postgresql://postgres:9@localhost:5432/dbass3"


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 70)
print("CSCI 341 - Assignment 3 - Part 2: SQL Queries")
print("=" * 70)

# ==================== 3. UPDATE SQL STATEMENTS ====================
print("\n" + "=" * 70)
print("3. UPDATE SQL STATEMENTS")
print("=" * 70)

# 3.1 Update phone number of Arman Armanov
print("\n3.1 Update phone number of Arman Armanov to +77773414141")
update_query_3_1 = text("""
    UPDATE "USER"
    SET phone_number = '+77773414141'
    WHERE given_name = 'Arman' AND surname = 'Armanov';
""")
result = session.execute(update_query_3_1)
session.commit()
print(f"Rows updated: {result.rowcount}")

# Verify the update
verify_query = text("""
    SELECT given_name, surname, phone_number 
    FROM "USER" 
    WHERE given_name = 'Arman' AND surname = 'Armanov';
""")
result = session.execute(verify_query)
for row in result:
    print(f"Verified: {row.given_name} {row.surname} - {row.phone_number}")

# 3.2 Add commission fee to caregivers' hourly rate
print("\n3.2 Add commission fee to Caregivers' hourly rate")
print("    - Add $0.3 if rate < $10")
print("    - Add 10% if rate >= $10")
update_query_3_2 = text("""
    UPDATE CAREGIVER
    SET hourly_rate = CASE
        WHEN hourly_rate < 10 THEN hourly_rate + 0.3
        ELSE hourly_rate * 1.10
    END;
""")
result = session.execute(update_query_3_2)
session.commit()
print(f"Rows updated: {result.rowcount}")

# Verify the update
verify_query = text("""
    SELECT c.caregiver_user_id, u.given_name, u.surname, c.hourly_rate
    FROM CAREGIVER c
    JOIN "USER" u ON c.caregiver_user_id = u.user_id
    ORDER BY c.caregiver_user_id
    LIMIT 5;
""")
result = session.execute(verify_query)
print("Sample updated rates:")
for row in result:
    print(f"  {row.given_name} {row.surname}: ${row.hourly_rate:.2f}")

# ==================== 4. DELETE SQL STATEMENTS ====================
print("\n" + "=" * 70)
print("4. DELETE SQL STATEMENTS")
print("=" * 70)

# 4.1 Delete jobs posted by Amina Aminova
print("\n4.1 Delete jobs posted by Amina Aminova")
delete_query_4_1 = text("""
    DELETE FROM JOB
    WHERE member_user_id IN (
        SELECT user_id 
        FROM "USER" 
        WHERE given_name = 'Amina' AND surname = 'Aminova'
    );
""")
result = session.execute(delete_query_4_1)
session.commit()
print(f"Jobs deleted: {result.rowcount}")

# 4.2 Delete all members who live on Kabanbay Batyr street
print("\n4.2 Delete all members who live on Kabanbay Batyr street")
delete_query_4_2 = text("""
    DELETE FROM "USER"
    WHERE user_id IN (
        SELECT m.member_user_id
        FROM MEMBER m
        JOIN ADDRESS a ON m.member_user_id = a.member_user_id
        WHERE a.street = 'Kabanbay Batyr'
    );
""")
result = session.execute(delete_query_4_2)
session.commit()
print(f"Members deleted: {result.rowcount}")

# ==================== 5. SIMPLE QUERIES ====================
print("\n" + "=" * 70)
print("5. SIMPLE QUERIES")
print("=" * 70)

# 5.1 Select caregiver and member names for accepted appointments
print("\n5.1 Caregiver and member names for accepted appointments:")
query_5_1 = text("""
    SELECT 
        uc.given_name AS caregiver_name,
        uc.surname AS caregiver_surname,
        um.given_name AS member_name,
        um.surname AS member_surname
    FROM APPOINTMENT a
    JOIN "USER" uc ON a.caregiver_user_id = uc.user_id
    JOIN "USER" um ON a.member_user_id = um.user_id
    WHERE a.status = 'Accepted';
""")
result = session.execute(query_5_1)
for row in result:
    print(f"  Caregiver: {row.caregiver_name} {row.caregiver_surname} | "
          f"Member: {row.member_name} {row.member_surname}")

# 5.2 List job ids that contain 'soft-spoken' in their other requirements
print("\n5.2 Job IDs with 'soft-spoken' in requirements:")
query_5_2 = text("""
    SELECT job_id, other_requirements
    FROM JOB
    WHERE other_requirements ILIKE '%soft-spoken%';
""")
result = session.execute(query_5_2)
for row in result:
    print(f"  Job ID: {row.job_id} - {row.other_requirements}")

# 5.3 List the work hours of all babysitter positions
print("\n5.3 Work hours of all babysitter appointments:")
query_5_3 = text("""
    SELECT a.appointment_id, a.work_hours, a.appointment_date
    FROM APPOINTMENT a
    JOIN CAREGIVER c ON a.caregiver_user_id = c.caregiver_user_id
    WHERE c.caregiving_type = 'Babysitter';
""")
result = session.execute(query_5_3)
for row in result:
    print(f"  Appointment {row.appointment_id}: {row.work_hours} hours on {row.appointment_date}")

# 5.4 List members looking for Elderly Care in Astana with "No pets." rule
print("\n5.4 Members seeking Elderly Care in Astana with 'No pets.' rule:")
query_5_4 = text("""
    SELECT u.given_name, u.surname, m.house_rules
    FROM MEMBER m
    JOIN "USER" u ON m.member_user_id = u.user_id
    JOIN JOB j ON m.member_user_id = j.member_user_id
    WHERE j.required_caregiving_type = 'Elderly Care'
    AND u.city = 'Astana'
    AND m.house_rules ILIKE '%No pets.%';
""")
result = session.execute(query_5_4)
for row in result:
    print(f"  {row.given_name} {row.surname} - Rules: {row.house_rules}")

# ==================== 6. COMPLEX QUERIES ====================
print("\n" + "=" * 70)
print("6. COMPLEX QUERIES")
print("=" * 70)

# 6.1 Count number of applicants for each job posted by a member
print("\n6.1 Number of applicants for each job:")
query_6_1 = text("""
    SELECT 
        j.job_id,
        j.required_caregiving_type,
        u.given_name || ' ' || u.surname AS posted_by,
        COUNT(ja.caregiver_user_id) AS applicant_count
    FROM JOB j
    JOIN "USER" u ON j.member_user_id = u.user_id
    LEFT JOIN JOB_APPLICATION ja ON j.job_id = ja.job_id
    GROUP BY j.job_id, j.required_caregiving_type, u.given_name, u.surname
    ORDER BY applicant_count DESC;
""")
result = session.execute(query_6_1)
for row in result:
    print(f"  Job {row.job_id} ({row.required_caregiving_type}) by {row.posted_by}: "
          f"{row.applicant_count} applicants")

# 6.2 Total hours spent by caregivers for all accepted appointments
print("\n6.2 Total hours worked by each caregiver (accepted appointments):")
query_6_2 = text("""
    SELECT 
        u.given_name || ' ' || u.surname AS caregiver_name,
        c.caregiving_type,
        SUM(a.work_hours) AS total_hours
    FROM CAREGIVER c
    JOIN "USER" u ON c.caregiver_user_id = u.user_id
    JOIN APPOINTMENT a ON c.caregiver_user_id = a.caregiver_user_id
    WHERE a.status = 'Accepted'
    GROUP BY u.given_name, u.surname, c.caregiving_type
    ORDER BY total_hours DESC;
""")
result = session.execute(query_6_2)
for row in result:
    print(f"  {row.caregiver_name} ({row.caregiving_type}): {row.total_hours} hours")

# 6.3 Average pay of caregivers based on accepted appointments
print("\n6.3 Average pay of caregivers (accepted appointments):")
query_6_3 = text("""
    SELECT 
        u.given_name || ' ' || u.surname AS caregiver_name,
        AVG(c.hourly_rate) AS avg_hourly_rate,
        COUNT(a.appointment_id) AS appointment_count
    FROM CAREGIVER c
    JOIN "USER" u ON c.caregiver_user_id = u.user_id
    JOIN APPOINTMENT a ON c.caregiver_user_id = a.caregiver_user_id
    WHERE a.status = 'Accepted'
    GROUP BY u.given_name, u.surname
    ORDER BY avg_hourly_rate DESC;
""")
result = session.execute(query_6_3)
for row in result:
    print(f"  {row.caregiver_name}: ${row.avg_hourly_rate:.2f}/hour "
          f"({row.appointment_count} appointments)")

# 6.4 Caregivers who earn above average based on accepted appointments
print("\n6.4 Caregivers earning above average:")
query_6_4 = text("""
    SELECT 
        u.given_name || ' ' || u.surname AS caregiver_name,
        c.hourly_rate,
        SUM(a.work_hours * c.hourly_rate) AS total_earnings
    FROM CAREGIVER c
    JOIN "USER" u ON c.caregiver_user_id = u.user_id
    JOIN APPOINTMENT a ON c.caregiver_user_id = a.caregiver_user_id
    WHERE a.status = 'Accepted'
    GROUP BY u.given_name, u.surname, c.hourly_rate
    HAVING SUM(a.work_hours * c.hourly_rate) > (
        SELECT AVG(total_earnings)
        FROM (
            SELECT SUM(a2.work_hours * c2.hourly_rate) AS total_earnings
            FROM CAREGIVER c2
            JOIN APPOINTMENT a2 ON c2.caregiver_user_id = a2.caregiver_user_id
            WHERE a2.status = 'Accepted'
            GROUP BY c2.caregiver_user_id
        ) AS earnings_subquery
    )
    ORDER BY total_earnings DESC;
""")
result = session.execute(query_6_4)
for row in result:
    print(f"  {row.caregiver_name}: ${row.total_earnings:.2f} total "
          f"(${row.hourly_rate:.2f}/hour)")

# ==================== 7. QUERY WITH DERIVED ATTRIBUTE ====================
print("\n" + "=" * 70)
print("7. QUERY WITH DERIVED ATTRIBUTE")
print("=" * 70)

print("\n7. Total cost for each accepted appointment:")
query_7 = text("""
    SELECT 
        a.appointment_id,
        uc.given_name || ' ' || uc.surname AS caregiver_name,
        um.given_name || ' ' || um.surname AS member_name,
        a.work_hours,
        c.hourly_rate,
        (a.work_hours * c.hourly_rate) AS total_cost
    FROM APPOINTMENT a
    JOIN CAREGIVER c ON a.caregiver_user_id = c.caregiver_user_id
    JOIN "USER" uc ON c.caregiver_user_id = uc.user_id
    JOIN "USER" um ON a.member_user_id = um.user_id
    WHERE a.status = 'Accepted'
    ORDER BY total_cost DESC;
""")
result = session.execute(query_7)
for row in result:
    print(f"  Appointment {row.appointment_id}: {row.caregiver_name} -> {row.member_name}")
    print(f"    {row.work_hours} hours × ${row.hourly_rate:.2f}/hour = ${row.total_cost:.2f}")

# ==================== 8. VIEW OPERATION ====================
print("\n" + "=" * 70)
print("8. VIEW OPERATION")
print("=" * 70)

print("\n8. Creating view for all job applications and applicants:")

# Create the view
create_view = text("""
    CREATE OR REPLACE VIEW job_applications_view AS
    SELECT 
        j.job_id,
        j.required_caregiving_type,
        j.other_requirements,
        um.given_name || ' ' || um.surname AS posted_by,
        uc.given_name || ' ' || uc.surname AS applicant_name,
        c.caregiving_type AS applicant_type,
        c.hourly_rate AS applicant_rate,
        ja.date_applied
    FROM JOB j
    JOIN "USER" um ON j.member_user_id = um.user_id
    JOIN JOB_APPLICATION ja ON j.job_id = ja.job_id
    JOIN CAREGIVER c ON ja.caregiver_user_id = c.caregiver_user_id
    JOIN "USER" uc ON c.caregiver_user_id = uc.user_id
    ORDER BY j.job_id, ja.date_applied;
""")
session.execute(create_view)
session.commit()
print("View 'job_applications_view' created successfully!")

# Query the view
print("\nQuerying the view:")
query_view = text("""
    SELECT * FROM job_applications_view;
""")
result = session.execute(query_view)
for row in result:
    print(f"\n  Job {row.job_id} ({row.required_caregiving_type}) posted by {row.posted_by}")
    print(f"    Applicant: {row.applicant_name} ({row.applicant_type}) - ${row.applicant_rate:.2f}/hour")
    print(f"    Applied on: {row.date_applied}")

print("\n" + "=" * 70)
print("ALL QUERIES COMPLETED SUCCESSFULLY!")
print("=" * 70)

# Close the session
session.close()
