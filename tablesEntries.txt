-- ==================== DROP EXISTING TABLES ====================
DROP TABLE IF EXISTS JOB_APPLICATION CASCADE;
DROP TABLE IF EXISTS APPOINTMENT CASCADE;
DROP TABLE IF EXISTS JOB CASCADE;
DROP TABLE IF EXISTS ADDRESS CASCADE;
DROP TABLE IF EXISTS MEMBER CASCADE;
DROP TABLE IF EXISTS CAREGIVER CASCADE;
DROP TABLE IF EXISTS "USER" CASCADE;

-- ==================== CREATE TABLES ====================

CREATE TABLE "USER" (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    phone_number VARCHAR(20),
    profile_description TEXT,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE CAREGIVER (
    caregiver_user_id INTEGER PRIMARY KEY,
    photo VARCHAR(500),
    gender VARCHAR(20),
    caregiving_type VARCHAR(50) NOT NULL,
    hourly_rate DECIMAL(10, 2),
    FOREIGN KEY (caregiver_user_id) REFERENCES "USER"(user_id) ON DELETE CASCADE
);

CREATE TABLE MEMBER (
    member_user_id INTEGER PRIMARY KEY,
    house_rules TEXT,
    dependent_description TEXT,
    FOREIGN KEY (member_user_id) REFERENCES "USER"(user_id) ON DELETE CASCADE
);

CREATE TABLE ADDRESS (
    member_user_id INTEGER PRIMARY KEY,
    house_number VARCHAR(20),
    street VARCHAR(200),
    town VARCHAR(100),
    FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id) ON DELETE CASCADE
);

CREATE TABLE JOB (
    job_id SERIAL PRIMARY KEY,
    member_user_id INTEGER NOT NULL,
    required_caregiving_type VARCHAR(50) NOT NULL,
    other_requirements TEXT,
    date_posted DATE NOT NULL,
    FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id) ON DELETE CASCADE
);

CREATE TABLE JOB_APPLICATION (
    caregiver_user_id INTEGER,
    job_id INTEGER,
    date_applied DATE NOT NULL,
    PRIMARY KEY (caregiver_user_id, job_id),
    FOREIGN KEY (caregiver_user_id) REFERENCES CAREGIVER(caregiver_user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES JOB(job_id) ON DELETE CASCADE
);

CREATE TABLE APPOINTMENT (
    appointment_id SERIAL PRIMARY KEY,
    caregiver_user_id INTEGER NOT NULL,
    member_user_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    work_hours INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (caregiver_user_id) REFERENCES CAREGIVER(caregiver_user_id) ON DELETE CASCADE,
    FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id) ON DELETE CASCADE
);

-- ==================== INSERT DATA ====================

-- Insert Users (Caregivers: 1-12, Members: 13-24)
INSERT INTO "USER" (email, given_name, surname, city, phone_number, profile_description, password) VALUES
-- Caregivers
('arman.armanov@email.com', 'Arman', 'Armanov', 'Astana', '+77771234567', 'Experienced babysitter with 5 years experience', 'pass123'),
('sara.jones@email.com', 'Sara', 'Jones', 'Almaty', '+77772345678', 'Certified elderly care specialist', 'pass123'),
('john.smith@email.com', 'John', 'Smith', 'Astana', '+77773456789', 'Fun playmate for children, degree in education', 'pass123'),
('maria.garcia@email.com', 'Maria', 'Garcia', 'Shymkent', '+77774567890', 'Compassionate elderly caregiver', 'pass123'),
('david.brown@email.com', 'David', 'Brown', 'Astana', '+77775678901', 'Reliable babysitter with first aid certification', 'pass123'),
('emma.wilson@email.com', 'Emma', 'Wilson', 'Almaty', '+77776789012', 'Patient and kind elderly care provider', 'pass123'),
('lucas.taylor@email.com', 'Lucas', 'Taylor', 'Astana', '+77777890123', 'Energetic playmate for kids', 'pass123'),
('sophia.anderson@email.com', 'Sophia', 'Anderson', 'Karaganda', '+77778901234', 'Professional babysitter, loves children', 'pass123'),
('oliver.thomas@email.com', 'Oliver', 'Thomas', 'Astana', '+77779012345', 'Experienced with dementia care', 'pass123'),
('ava.martinez@email.com', 'Ava', 'Martinez', 'Almaty', '+77770123456', 'Creative playmate and tutor', 'pass123'),
('william.lee@email.com', 'William', 'Lee', 'Astana', '+77771122334', 'Gentle elderly care specialist', 'pass123'),
('mia.white@email.com', 'Mia', 'White', 'Shymkent', '+77772233445', 'Babysitter with pediatric nursing background', 'pass123'),
-- Members
('amina.aminova@email.com', 'Amina', 'Aminova', 'Astana', '+77781234567', 'Mother of two lovely children', 'pass456'),
('nursultan.nurs@email.com', 'Nursultan', 'Nursultanov', 'Almaty', '+77782345678', 'Looking for elderly care for my mother', 'pass456'),
('dana.danina@email.com', 'Dana', 'Danina', 'Astana', '+77783456789', 'Need playmate for my energetic son', 'pass456'),
('aidar.aidarov@email.com', 'Aidar', 'Aidarov', 'Shymkent', '+77784567890', 'Seeking babysitter for weekends', 'pass456'),
('laura.laurova@email.com', 'Laura', 'Laurova', 'Astana', '+77785678901', 'Need caregiver for elderly father', 'pass456'),
('timur.timurov@email.com', 'Timur', 'Timurov', 'Almaty', '+77786789012', 'Looking for reliable babysitter', 'pass456'),
('zarina.zarina@email.com', 'Zarina', 'Zarinova', 'Astana', '+77787890123', 'Need elderly care professional', 'pass456'),
('aslan.aslanov@email.com', 'Aslan', 'Aslanov', 'Karaganda', '+77788901234', 'Seeking playmate for my daughter', 'pass456'),
('madina.madina@email.com', 'Madina', 'Madinova', 'Astana', '+77789012345', 'Looking for weekend babysitter', 'pass456'),
('erik.erikov@email.com', 'Erik', 'Erikov', 'Almaty', '+77780123456', 'Need caregiver for grandmother', 'pass456'),
('aisha.aisha@email.com', 'Aisha', 'Aishova', 'Astana', '+77781122334', 'Mother seeking part-time babysitter', 'pass456'),
('beka.bekov@email.com', 'Beka', 'Bekov', 'Shymkent', '+77782233445', 'Need elderly care for father', 'pass456');

-- Insert Caregivers
INSERT INTO CAREGIVER (caregiver_user_id, photo, gender, caregiving_type, hourly_rate) VALUES
(1, 'photos/arman.jpg', 'Male', 'Babysitter', 8.50),
(2, 'photos/sara.jpg', 'Female', 'Elderly Care', 12.00),
(3, 'photos/john.jpg', 'Male', 'Playmate', 7.00),
(4, 'photos/maria.jpg', 'Female', 'Elderly Care', 11.50),
(5, 'photos/david.jpg', 'Male', 'Babysitter', 9.00),
(6, 'photos/emma.jpg', 'Female', 'Elderly Care', 13.00),
(7, 'photos/lucas.jpg', 'Male', 'Playmate', 6.50),
(8, 'photos/sophia.jpg', 'Female', 'Babysitter', 8.00),
(9, 'photos/oliver.jpg', 'Male', 'Elderly Care', 14.00),
(10, 'photos/ava.jpg', 'Female', 'Playmate', 7.50),
(11, 'photos/william.jpg', 'Male', 'Elderly Care', 12.50),
(12, 'photos/mia.jpg', 'Female', 'Babysitter', 9.50);

-- Insert Members
INSERT INTO MEMBER (member_user_id, house_rules, dependent_description) VALUES
(13, 'No smoking. No pets.', 'I have a 5-year-old son who likes painting and playing outdoors'),
(14, 'Must be punctual. No pets.', 'My 78-year-old mother needs assistance with daily activities'),
(15, 'Clean environment required.', '7-year-old boy, energetic and loves sports'),
(16, 'No smoking.', 'Twin girls aged 3, very active'),
(17, 'Must follow medication schedule. No pets.', '82-year-old father with mobility issues'),
(18, 'Punctuality important.', '4-year-old daughter, loves reading'),
(19, 'No pets. Must be gentle.', 'Grandmother aged 85, needs companionship'),
(20, 'Clean and organized.', '6-year-old girl who enjoys arts and crafts'),
(21, 'No smoking. Must be reliable.', 'Two boys aged 8 and 10'),
(22, 'Patience required. No pets.', '90-year-old grandmother, hard of hearing'),
(23, 'Flexible hours needed.', '5-year-old boy, loves building blocks'),
(24, 'Must be experienced. No pets.', 'Father aged 75, recovering from surgery');

-- Insert Addresses
INSERT INTO ADDRESS (member_user_id, house_number, street, town) VALUES
(13, '15', 'Kabanbay Batyr', 'Yesil District'),
(14, '23', 'Respublika Avenue', 'Almaly District'),
(15, '8', 'Mangilik El', 'Yesil District'),
(16, '45', 'Turan Avenue', 'Saryarka District'),
(17, '12', 'Kabanbay Batyr', 'Yesil District'),
(18, '67', 'Abay Street', 'Bostandyk District'),
(19, '34', 'Dostyk Avenue', 'Yesil District'),
(20, '89', 'Zheltoqsan Street', 'Saryarka District'),
(21, '56', 'Tauelsizdik Avenue', 'Yesil District'),
(22, '78', 'Furmanov Street', 'Turksib District'),
(23, '21', 'Syganak Street', 'Yesil District'),
(24, '43', 'Ablai Khan Avenue', 'Saryarka District');

-- Insert Jobs
INSERT INTO JOB (member_user_id, required_caregiving_type, other_requirements, date_posted) VALUES
(13, 'Babysitter', 'Must be patient and soft-spoken. Weekdays 09:00-12:00', '2025-11-01'),
(14, 'Elderly Care', 'Experience with mobility assistance required. Daily care needed', '2025-11-02'),
(15, 'Playmate', 'Should enjoy outdoor activities. Weekends only', '2025-11-03'),
(16, 'Babysitter', 'Experience with twins preferred. Soft-spoken and gentle', '2025-11-04'),
(17, 'Elderly Care', 'Must know medication management. Daily 12:00-15:00', '2025-11-05'),
(18, 'Babysitter', 'Love for reading required. Part-time weekdays', '2025-11-06'),
(19, 'Elderly Care', 'Companionship and light housekeeping. Weekly visits', '2025-11-07'),
(20, 'Playmate', 'Arts and crafts skills needed. Weekends preferred', '2025-11-08'),
(21, 'Babysitter', 'Must handle two children. Soft-spoken and energetic', '2025-11-09'),
(22, 'Elderly Care', 'Patience required, experience with hearing impairment', '2025-11-10'),
(13, 'Babysitter', 'Evening care needed. Must be reliable and soft-spoken', '2025-11-11'),
(15, 'Playmate', 'Sports activities supervision. Daily after school', '2025-11-12');

-- Insert Job Applications
INSERT INTO JOB_APPLICATION (caregiver_user_id, job_id, date_applied) VALUES
(1, 1, '2025-11-02'),
(5, 1, '2025-11-02'),
(8, 1, '2025-11-03'),
(2, 2, '2025-11-03'),
(4, 2, '2025-11-03'),
(3, 3, '2025-11-04'),
(7, 3, '2025-11-04'),
(10, 3, '2025-11-04'),
(1, 4, '2025-11-05'),
(8, 4, '2025-11-05'),
(12, 4, '2025-11-05'),
(6, 5, '2025-11-06'),
(9, 5, '2025-11-06'),
(5, 6, '2025-11-07'),
(12, 6, '2025-11-07');

-- Insert Appointments
INSERT INTO APPOINTMENT (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status) VALUES
(1, 13, '2025-11-25', '09:00', 3, 'Accepted'),
(2, 14, '2025-11-26', '10:00', 4, 'Accepted'),
(3, 15, '2025-11-27', '14:00', 2, 'Pending'),
(5, 16, '2025-11-28', '08:00', 5, 'Accepted'),
(6, 17, '2025-11-29', '12:00', 3, 'Accepted'),
(8, 18, '2025-11-30', '15:00', 2, 'Declined'),
(9, 19, '2025-12-01', '11:00', 4, 'Accepted'),
(10, 20, '2025-12-02', '13:00', 3, 'Accepted'),
(1, 21, '2025-12-03', '09:00', 4, 'Accepted'),
(11, 22, '2025-12-04', '10:00', 5, 'Pending'),
(12, 23, '2025-12-05', '14:00', 3, 'Accepted'),
(4, 24, '2025-12-06', '12:00', 4, 'Accepted');