-- =====================================================
--  DRIVING SCHOOL - FULL SETUP SCRIPT
--  Creates mydb, all 8 tables, and loads the sample data.
--  Safe to re-run: it drops and recreates mydb.
-- =====================================================
DROP DATABASE IF EXISTS mydb;
CREATE DATABASE mydb;
USE mydb;

CREATE TABLE Student (
  StudentID        INT NOT NULL AUTO_INCREMENT,
  FirstName        VARCHAR(50)  NOT NULL,
  LastName         VARCHAR(50)  NOT NULL,
  Phone            VARCHAR(20)  NOT NULL,
  Email            VARCHAR(100) NOT NULL,
  RegistrationDate DATE NOT NULL,
  PRIMARY KEY (StudentID)
);

CREATE TABLE Instructor (
  InstructorID    INT NOT NULL AUTO_INCREMENT,
  InstructorName  VARCHAR(100) NOT NULL,
  Phone           VARCHAR(20)  NOT NULL,
  HireDate        DATE NOT NULL,
  ExperienceYears INT  NOT NULL,
  PRIMARY KEY (InstructorID)
);

CREATE TABLE Vehicle (
  VehicleID    INT NOT NULL AUTO_INCREMENT,
  Model        VARCHAR(50) NOT NULL,
  PlateNumber  VARCHAR(20) NOT NULL,
  Year         INT NOT NULL,
  InstructorID INT NULL,
  PRIMARY KEY (VehicleID),
  FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID)
);

CREATE TABLE Package (
  PackageID       INT NOT NULL AUTO_INCREMENT,
  PackageName     VARCHAR(50)  NOT NULL,
  Description     VARCHAR(255) NULL,
  NumberOfLessons INT NOT NULL,
  Price           DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (PackageID)
);

CREATE TABLE StudentPackage (
  StudentPackageID INT NOT NULL AUTO_INCREMENT,
  StudentID        INT NOT NULL,
  PackageID        INT NOT NULL,
  PurchaseDate     DATE NOT NULL DEFAULT (CURRENT_DATE),
  PRIMARY KEY (StudentPackageID),
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
  FOREIGN KEY (PackageID) REFERENCES Package(PackageID)
);

CREATE TABLE Lesson (
  LessonID      INT NOT NULL AUTO_INCREMENT,
  StudentID     INT NOT NULL,
  InstructorID  INT NOT NULL,
  VehicleID     INT NOT NULL,
  LessonDate    DATE NOT NULL,
  DurationHours INT  NOT NULL,
  PRIMARY KEY (LessonID),
  FOREIGN KEY (StudentID)    REFERENCES Student(StudentID),
  FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID),
  FOREIGN KEY (VehicleID)    REFERENCES Vehicle(VehicleID)
);

CREATE TABLE Exam (
  ExamID    INT NOT NULL AUTO_INCREMENT,
  StudentID INT NOT NULL,
  ExamDate  DATE NOT NULL,
  Score     INT  NOT NULL,
  Result    VARCHAR(20) NOT NULL,
  PRIMARY KEY (ExamID),
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

CREATE TABLE Payment (
  PaymentID     INT NOT NULL AUTO_INCREMENT,
  StudentID     INT NOT NULL,
  Amount        DECIMAL(8,2) NOT NULL,
  PaymentDate   DATE NOT NULL,
  PaymentMethod VARCHAR(20)  NOT NULL,
  PRIMARY KEY (PaymentID),
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- =====================================
-- SAMPLE DATA (from SQL.sql)
-- =====================================
-- -- INSTRUCTORS
-- =====================================

INSERT INTO Instructor
(InstructorID, InstructorName, Phone, HireDate, ExperienceYears)
VALUES
(1,'Marco Rossi','3331111111','2020-01-15',8),
(2,'Luca Bianchi','3331111112','2019-03-20',10),
(3,'Giulia Romano','3331111113','2021-06-10',5),
(4,'Andrea Conti','3331111114','2018-09-12',12),
(5,'Francesca Ricci','3331111115','2022-02-01',4);

-- =====================================
-- VEHICLES
-- =====================================
INSERT INTO Vehicle
(VehicleID, Model, PlateNumber, Year, InstructorID)
VALUES
(1,'Toyota Yaris','AB123CD',2022,1),
(2,'Fiat Panda','EF456GH',2021,2),
(3,'Volkswagen Polo','IJ789KL',2023,3),
(4,'Renault Clio','MN012OP',2022,4);

-- =====================================
-- PACKAGES
-- =====================================
INSERT INTO Package
(PackageID, PackageName, NumberOfLessons, Price)
VALUES
(1,'Basic',10,300),
(2,'Standard',15,420),
(3,'Premium',20,550),
(4,'Advanced',25,680),
(5,'VIP',30,800);


-- =====================================
-- STUDENTS
-- =====================================
INSERT INTO Student
(StudentID, FirstName, LastName, Phone, Email, RegistrationDate)
VALUES
(1,'Ali','Ahmadi','3501000001','ali.ahmadi@email.com','2025-01-10'),
(2,'Sara','Mohammadi','3501000002','sara.m@email.com','2025-01-12'),
(3,'Reza','Karimi','3501000003','reza.k@email.com','2025-01-15'),
(4,'Fatima','Hosseini','3501000004','fatima.h@email.com','2025-01-18'),
(5,'Amir','Rahimi','3501000005','amir.r@email.com','2025-01-20'),
(6,'Neda','Jafari','3501000006','neda.j@email.com','2025-01-22'),
(7,'Omid','Azizi','3501000007','omid.a@email.com','2025-01-25'),
(8,'Maryam','Safari','3501000008','maryam.s@email.com','2025-01-27'),
(9,'Hossein','Moradi','3501000009','hossein.m@email.com','2025-02-01'),
(10,'Leila','Kiani','3501000010','leila.k@email.com','2025-02-03'),
(11,'Arman','Najafi','3501000011','arman.n@email.com','2025-02-05'),
(12,'Zahra','Ebrahimi','3501000012','zahra.e@email.com','2025-02-08'),
(13,'Saeed','Yousefi','3501000013','saeed.y@email.com','2025-02-10'),
(14,'Parisa','Ghasemi','3501000014','parisa.g@email.com','2025-02-12'),
(15,'Mehdi','Shahriari','3501000015','mehdi.s@email.com','2025-02-15'),
(16,'Elena','Rossi','3501000016','elena.r@email.com','2025-02-18'),
(17,'Luca','Bianchi','3501000017','luca.b@email.com','2025-02-20'),
(18,'Marco','Conti','3501000018','marco.c@email.com','2025-02-22'),
(19,'Giulia','Romano','3501000019','giulia.r@email.com','2025-02-25'),
(20,'Andrea','Ricci','3501000020','andrea.r@email.com','2025-02-28'),
(21,'Anna','Ferrari','3501000021','anna.f@email.com','2025-03-01'),
(22,'Davide','Greco','3501000022','davide.g@email.com','2025-03-03'),
(23,'Francesca','Lombardi','3501000023','francesca.l@email.com','2025-03-05'),
(24,'Matteo','Moretti','3501000024','matteo.m@email.com','2025-03-08'),
(25,'Chiara','Marino','3501000025','chiara.m@email.com','2025-03-10'),
(26,'Simone','Costa','3501000026','simone.c@email.com','2025-03-12'),
(27,'Valentina','Fontana','3501000027','valentina.f@email.com','2025-03-15'),
(28,'Alessandro','Galli','3501000028','alessandro.g@email.com','2025-03-18'),
(29,'Martina','Rinaldi','3501000029','martina.r@email.com','2025-03-20'),
(30,'Federico','Villa','3501000030','federico.v@email.com','2025-03-22');

-- =====================================
-- STUDENT PACKAGES
-- =====================================

INSERT INTO StudentPackage
(StudentPackageID, StudentID, PackageID, PurchaseDate)
VALUES
(1,1,1,'2025-01-10'),
(2,2,2,'2025-01-12'),
(3,3,3,'2025-01-15'),
(4,4,1,'2025-01-18'),
(5,5,2,'2025-01-20'),
(6,6,3,'2025-01-22'),
(7,7,4,'2025-01-25'),
(8,8,5,'2025-01-27'),
(9,9,1,'2025-02-01'),
(10,10,2,'2025-02-03'),
(11,11,3,'2025-02-05'),
(12,12,4,'2025-02-08'),
(13,13,5,'2025-02-10'),
(14,14,1,'2025-02-12'),
(15,15,2,'2025-02-15'),
(16,16,3,'2025-02-18'),
(17,17,4,'2025-02-20'),
(18,18,5,'2025-02-22'),
(19,19,1,'2025-02-25'),
(20,20,2,'2025-02-28'),
(21,21,3,'2025-03-01'),
(22,22,4,'2025-03-03'),
(23,23,5,'2025-03-05'),
(24,24,1,'2025-03-08'),
(25,25,2,'2025-03-10'),
(26,26,3,'2025-03-12'),
(27,27,4,'2025-03-15'),
(28,28,5,'2025-03-18'),
(29,29,1,'2025-03-20'),
(30,30,2,'2025-03-22');


-- =====================================
-- EXAMS
-- =====================================

INSERT INTO Exam
(ExamID, StudentID, ExamDate, Score, Result)
VALUES
(1,1,'2025-04-01',88,'Passed'),
(2,7,'2025-04-02',91,'Passed'),
(3,3,'2025-04-03',74,'Passed'),
(4,5,'2025-04-04',69,'Passed'),
(5,9,'2025-04-05',58,'Failed'),
(6,4,'2025-04-06',62,'Passed'),
(7,10,'2025-04-07',55,'Failed'),
(8,25,'2025-04-08',77,'Passed'),
(9,2,'2025-04-09',81,'Passed'),
(10,6,'2025-04-10',64,'Passed'),
(11,8,'2025-04-11',52,'Failed'),
(12,13,'2025-04-12',72,'Passed'),
(13,19,'2025-04-13',68,'Passed'),
(14,22,'2025-04-14',59,'Failed'),
(15,23,'2025-04-15',83,'Passed'),
(16,27,'2025-04-16',75,'Passed'),
(17,29,'2025-04-17',61,'Passed');


-- =====================================
-- PAYMENTS
-- =====================================

INSERT INTO Payment
(PaymentID, StudentID, Amount, PaymentDate, PaymentMethod)
VALUES
(1,1,300,'2025-01-10','Card'),
(2,2,420,'2025-01-12','Cash'),
(3,3,550,'2025-01-15','Card'),
(4,4,300,'2025-01-18','Bank Transfer'),
(5,5,420,'2025-01-20','Card'),
(6,6,550,'2025-01-22','Cash'),
(7,7,680,'2025-01-25','Card'),
(8,8,800,'2025-01-27','Bank Transfer'),
(9,9,300,'2025-02-01','Cash'),
(10,10,420,'2025-02-03','Card'),
(11,11,550,'2025-02-05','Card'),
(12,12,680,'2025-02-08','Cash'),
(13,13,800,'2025-02-10','Bank Transfer'),
(14,14,300,'2025-02-12','Card'),
(15,15,420,'2025-02-15','Cash'),
(16,16,550,'2025-02-18','Card'),
(17,17,680,'2025-02-20','Bank Transfer'),
(18,18,800,'2025-02-22','Card'),
(19,19,300,'2025-02-25','Cash'),
(20,20,420,'2025-02-28','Card'),
(21,21,550,'2025-03-01','Cash'),
(22,22,680,'2025-03-03','Card'),
(23,23,800,'2025-03-05','Bank Transfer'),
(24,24,300,'2025-03-08','Cash'),
(25,25,420,'2025-03-10','Card'),
(26,26,550,'2025-03-12','Cash'),
(27,27,680,'2025-03-15','Card'),
(28,28,800,'2025-03-18','Bank Transfer'),
(29,29,300,'2025-03-20','Cash'),
(30,30,420,'2025-03-22','Card');

-- =====================================
-- LESSONS
-- =====================================

INSERT INTO Lesson
(LessonID, StudentID, InstructorID, VehicleID, LessonDate, DurationHours)
VALUES
(1,1,1,1,'2025-02-01',2),
(2,2,2,2,'2025-02-01',2),
(3,3,3,3,'2025-02-02',1),
(4,4,4,4,'2025-02-02',2),
(5,5,5,1,'2025-02-03',2),
(6,6,1,2,'2025-02-03',1),
(7,7,2,3,'2025-02-04',2),
(8,8,3,4,'2025-02-04',2),
(9,9,4,1,'2025-02-05',1),
(10,10,5,2,'2025-02-05',2),
(11,11,1,3,'2025-02-06',2),
(12,12,2,4,'2025-02-06',1),
(13,13,3,1,'2025-02-07',2),
(14,14,4,2,'2025-02-07',2),
(15,15,5,3,'2025-02-08',1),
(16,16,1,4,'2025-02-08',2),
(17,17,2,1,'2025-02-09',2),
(18,18,3,2,'2025-02-09',1),
(19,19,4,3,'2025-02-10',2),
(20,20,5,4,'2025-02-10',2),
(21,21,1,1,'2025-02-11',1),
(22,22,2,2,'2025-02-11',2),
(23,23,3,3,'2025-02-12',2),
(24,24,4,4,'2025-02-12',1),
(25,25,5,1,'2025-02-13',2),
(26,26,1,2,'2025-02-13',2),
(27,27,2,3,'2025-02-14',1),
(28,28,3,4,'2025-02-14',2),
(29,29,4,1,'2025-02-15',2),
(30,30,5,2,'2025-02-15',1),
(31,1,1,3,'2025-02-16',2),
(32,2,2,4,'2025-02-16',1),
(33,3,3,1,'2025-02-17',2),
(34,4,4,2,'2025-02-17',2),
(35,5,5,3,'2025-02-18',1),
(36,6,1,4,'2025-02-18',2),
(37,7,2,1,'2025-02-19',2),
(38,8,3,2,'2025-02-19',1),
(39,9,4,3,'2025-02-20',2),
(40,10,5,4,'2025-02-20',2),
(41,11,1,1,'2025-02-21',1),
(42,12,2,2,'2025-02-21',2),
(43,13,3,3,'2025-02-22',2),
(44,14,4,4,'2025-02-22',1),
(45,15,5,1,'2025-02-23',2),
(46,16,1,2,'2025-02-23',2),
(47,17,2,3,'2025-02-24',1),
(48,18,3,4,'2025-02-24',2),
(49,19,4,1,'2025-02-25',2),
(50,20,5,2,'2025-02-25',1);

INSERT INTO Lesson
(LessonID, StudentID, InstructorID, VehicleID, LessonDate, DurationHours)
VALUES
(51,21,1,3,'2025-03-01',2),
(52,22,2,4,'2025-03-01',3),
(53,23,3,1,'2025-03-02',2),
(54,24,4,2,'2025-03-02',2),
(55,25,5,3,'2025-03-03',3),
(56,26,1,4,'2025-03-03',2),
(57,27,2,1,'2025-03-04',3),
(58,28,3,2,'2025-03-04',2),
(59,29,4,3,'2025-03-05',2),
(60,30,5,4,'2025-03-05',3),
(61,1,1,1,'2025-03-06',3),
(62,2,2,2,'2025-03-06',2),
(63,3,3,3,'2025-03-07',3),
(64,4,4,4,'2025-03-07',2),
(65,5,5,1,'2025-03-08',3),
(66,6,1,2,'2025-03-08',2),
(67,7,2,3,'2025-03-09',3),
(68,8,3,4,'2025-03-09',2),
(69,9,4,1,'2025-03-10',3),
(70,10,5,2,'2025-03-10',2),
(71,11,1,3,'2025-03-11',3),
(72,12,2,4,'2025-03-11',2),
(73,13,3,1,'2025-03-12',3),
(74,14,4,2,'2025-03-12',2),
(75,15,5,3,'2025-03-13',3),
(76,16,1,4,'2025-03-13',2),
(77,17,2,1,'2025-03-14',3),
(78,18,3,2,'2025-03-14',2),
(79,19,4,3,'2025-03-15',3),
(80,20,5,4,'2025-03-15',2),
(81,21,1,1,'2025-03-16',3),
(82,22,2,2,'2025-03-16',2),
(83,23,3,3,'2025-03-17',3),
(84,24,4,4,'2025-03-17',2),
(85,25,5,1,'2025-03-18',3),
(86,26,1,2,'2025-03-18',2),
(87,27,2,3,'2025-03-19',3),
(88,28,3,4,'2025-03-19',2),
(89,29,4,1,'2025-03-20',3),
(90,30,5,2,'2025-03-20',2),
(91,1,1,3,'2025-03-21',3),
(92,2,2,4,'2025-03-21',2),
(93,3,3,1,'2025-03-22',3),
(94,4,4,2,'2025-03-22',2),
(95,5,5,3,'2025-03-23',3),
(96,6,1,4,'2025-03-23',2),
(97,7,2,1,'2025-03-24',3),
(98,8,3,2,'2025-03-24',2),
(99,9,4,3,'2025-03-25',3),
(100,10,5,4,'2025-03-25',2);

SELECT COUNT(*) AS TotalStudents FROM Student;
