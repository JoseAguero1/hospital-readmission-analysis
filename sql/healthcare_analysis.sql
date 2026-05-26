-- ============================================================
--  Hospital Patient Readmission Analysis — SQL Portfolio Project
--  Author : Jose
--  Tools  : SQLite (compatible with PostgreSQL)
--  Table  : patients (loaded from healthcare_patients.csv)
-- ============================================================
--
--  TABLE SCHEMA
--  ─────────────────────────────────────────────────────────
--  patients
--    patient_id              TEXT PRIMARY KEY
--    age                     TEXT   -- bracket e.g. '[50-60)'
--    gender                  TEXT
--    race                    TEXT
--    admission_type          TEXT
--    discharge_disposition   TEXT
--    admission_source        TEXT
--    department              TEXT
--    primary_diagnosis       TEXT
--    time_in_hospital        INT
--    num_lab_procedures      INT
--    num_procedures          INT
--    num_medications         INT
--    num_diagnoses           INT
--    num_outpatient_visits   INT
--    num_inpatient_visits    INT
--    num_emergency_visits    INT
--    insulin                 TEXT
--    change_of_meds          TEXT
--    diabetes_med            TEXT
--    hba1c_result            TEXT
--    glucose_serum           TEXT
--    readmitted_30days       INT    -- 0 | 1
--    readmission_risk_score  REAL
-- ============================================================


-- ============================================================
-- Q1 · Overall readmission summary
--      Skills: aggregate functions, ROUND, CAST
-- ============================================================
SELECT
    COUNT(*)                                             AS total_patients,
    SUM(readmitted_30days)                               AS total_readmitted,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmission_rate_pct,
    ROUND(AVG(time_in_hospital), 1)                      AS avg_length_of_stay,
    ROUND(AVG(num_medications), 1)                       AS avg_medications,
    ROUND(AVG(num_diagnoses), 1)                         AS avg_diagnoses
FROM patients;


-- ============================================================
-- Q2 · Readmission rate by department
--      Skills: GROUP BY, HAVING, ORDER BY aggregate
-- ============================================================
SELECT
    department,
    COUNT(*)                                              AS total_patients,
    SUM(readmitted_30days)                                AS readmitted,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct,
    ROUND(AVG(time_in_hospital), 1)                       AS avg_los_days
FROM patients
GROUP BY department
ORDER BY readmit_rate_pct DESC;


-- ============================================================
-- Q3 · Readmission rate by primary diagnosis
--      Skills: GROUP BY, conditional aggregation
-- ============================================================
SELECT
    primary_diagnosis,
    COUNT(*)                                              AS total_patients,
    SUM(readmitted_30days)                                AS readmitted,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct,
    ROUND(AVG(num_medications), 1)                        AS avg_medications,
    ROUND(AVG(num_diagnoses), 1)                          AS avg_diagnoses
FROM patients
GROUP BY primary_diagnosis
ORDER BY readmit_rate_pct DESC;


-- ============================================================
-- Q4 · High risk patients (multiple risk factors)
--      Skills: WHERE with multiple conditions, CASE WHEN risk tier
-- ============================================================
SELECT
    patient_id,
    age,
    department,
    primary_diagnosis,
    time_in_hospital,
    num_inpatient_visits,
    num_emergency_visits,
    hba1c_result,
    readmission_risk_score,
    CASE
        WHEN readmission_risk_score >= 40 THEN 'High Risk'
        WHEN readmission_risk_score >= 25 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_tier,
    readmitted_30days
FROM patients
WHERE num_inpatient_visits > 1
  AND hba1c_result = '>8'
  AND admission_type = 'Emergency'
ORDER BY readmission_risk_score DESC
LIMIT 20;


-- ============================================================
-- Q5 · Readmission rate by admission type and length of stay bucket
--      Skills: CASE WHEN bucketing, GROUP BY multiple columns
-- ============================================================
SELECT
    admission_type,
    CASE
        WHEN time_in_hospital <= 2  THEN '1-2 days'
        WHEN time_in_hospital <= 5  THEN '3-5 days'
        WHEN time_in_hospital <= 9  THEN '6-9 days'
        ELSE '10+ days'
    END AS los_bucket,
    COUNT(*)                                              AS patients,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct
FROM patients
GROUP BY admission_type, los_bucket
ORDER BY admission_type, readmit_rate_pct DESC;


-- ============================================================
-- Q6 · Impact of HbA1c result on readmission
--      Skills: GROUP BY, ORDER BY CASE for custom sort
-- ============================================================
SELECT
    hba1c_result,
    COUNT(*)                                              AS patients,
    SUM(readmitted_30days)                                AS readmitted,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct,
    ROUND(AVG(time_in_hospital), 1)                       AS avg_los
FROM patients
GROUP BY hba1c_result
ORDER BY CASE hba1c_result
    WHEN '>8'     THEN 1
    WHEN '>7'     THEN 2
    WHEN 'Normal' THEN 3
    ELSE 4
END;


-- ============================================================
-- Q7 · Department readmission ranking with window function
--      Skills: RANK() OVER, CTE, window functions
-- ============================================================
WITH dept_stats AS (
    SELECT
        department,
        COUNT(*)                                              AS total_patients,
        SUM(readmitted_30days)                                AS readmitted,
        ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct,
        ROUND(AVG(time_in_hospital), 1)                       AS avg_los
    FROM patients
    GROUP BY department
)
SELECT
    department,
    total_patients,
    readmitted,
    readmit_rate_pct,
    avg_los,
    RANK() OVER (ORDER BY readmit_rate_pct DESC) AS readmit_rank
FROM dept_stats
ORDER BY readmit_rank;


-- ============================================================
-- Q8 · Patient risk segmentation summary
--      Skills: CASE WHEN, GROUP BY, percentage of total
-- ============================================================
WITH risk_segments AS (
    SELECT
        CASE
            WHEN readmission_risk_score >= 40 THEN 'High Risk'
            WHEN readmission_risk_score >= 25 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS risk_tier,
        readmitted_30days,
        time_in_hospital,
        num_medications
    FROM patients
)
SELECT
    risk_tier,
    COUNT(*)                                              AS patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)    AS pct_of_total,
    SUM(readmitted_30days)                                AS readmitted,
    ROUND(AVG(CAST(readmitted_30days AS FLOAT)) * 100, 1) AS readmit_rate_pct,
    ROUND(AVG(time_in_hospital), 1)                       AS avg_los,
    ROUND(AVG(num_medications), 1)                        AS avg_medications
FROM risk_segments
GROUP BY risk_tier
ORDER BY CASE risk_tier
    WHEN 'High Risk'   THEN 1
    WHEN 'Medium Risk' THEN 2
    ELSE 3
END;
