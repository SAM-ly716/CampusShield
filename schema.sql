CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  pw_hash TEXT,
  role TEXT          -- 'admin' | 'registrar' | 'student'
);
CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  name TEXT, email TEXT, dob TEXT, major TEXT, gpa REAL
);
CREATE TABLE attendance (
  id INTEGER PRIMARY KEY,
  student_id INTEGER, course TEXT, status TEXT, date TEXT
);
INSERT INTO users (username, pw_hash, role) VALUES
  ('admin','PLACEHOLDER','admin'),
  ('registrar','PLACEHOLDER','registrar'),
  ('student1','PLACEHOLDER','student');
INSERT INTO students (name,email,dob,major,gpa) VALUES
  ('Alice Fakename','alice@uni.test','2003-04-12','CS',3.4),
  ('Bob Synthetic','bob@uni.test','2002-11-01','EE',2.9);
