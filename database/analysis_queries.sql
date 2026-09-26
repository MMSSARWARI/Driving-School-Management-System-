-- Analysis queries used in the report (Section 5.4).
-- Run setup_database.sql first.
USE mydb;

-- ============================================
-- QUERY 1
-- Most Profitable Package (The packages with highest revenue= price of package*how many times purchased)
-- 
-- ============================================

SELECT
    p.PackageName,
    COUNT(sp.StudentID) AS TotalStudents,
    SUM(pay.Amount) AS TotalRevenue
FROM Package p
JOIN StudentPackage sp
    ON p.PackageID = sp.PackageID
JOIN Payment pay
    ON sp.StudentID = pay.StudentID
GROUP BY p.PackageID
ORDER BY TotalRevenue DESC;

-- ============================================
-- QUERY 2
-- Instructor Teaching Hours
-- ============================================
SELECT
    i.InstructorName,
    SUM(l.DurationHours) AS TotalHours
FROM Instructor i
JOIN Lesson l
    ON i.InstructorID = l.InstructorID
GROUP BY i.InstructorID
ORDER BY TotalHours DESC;



-- ============================================
-- QUERY 3
-- Exam Results
-- ============================================
SELECT
    Result,
    COUNT(*) AS TotalStudents
FROM Exam
GROUP BY Result;


-- ============================================
-- QUERY 4
-- Most Used Vehicle
-- ============================================

SELECT
    v.VehicleID,
    v.Model,
    COUNT(l.LessonID) AS TotalLessons,
    SUM(l.DurationHours) AS TotalHoursUsed
FROM Vehicle v
JOIN Lesson l
    ON v.VehicleID = l.VehicleID
GROUP BY v.VehicleID
ORDER BY TotalHoursUsed DESC;

-- ============================================
-- QUERY 5
-- Package Effectiveness
-- ============================================
SELECT
    p.PackageName,
    COUNT(e.ExamID) AS ExamsTaken,
    SUM(CASE WHEN e.Result='Passed' THEN 1 ELSE 0 END) AS PassedStudents,
    ROUND(
        SUM(CASE WHEN e.Result='Passed' THEN 1 ELSE 0 END)
        *100.0/
        COUNT(e.ExamID),
        2
    ) AS PassRate
FROM Package p
JOIN StudentPackage sp
    ON p.PackageID = sp.PackageID
JOIN Exam e
    ON sp.StudentID = e.StudentID
GROUP BY p.PackageID;
