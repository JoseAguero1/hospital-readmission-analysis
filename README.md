Here are all three READMEs — copy and paste each one into a new file called README.md in each repo folder.

FINANCE — personal-finance-analysis/README.md
markdown# Personal Finance Analysis — 2023–2024

## Overview
End-to-end data analysis project analyzing 2 years of personal
finance transactions across 10 spending categories.

**Tools used:** Python · SQL (SQLite) · Power BI · Excel

## Key Findings
- Average savings rate of 26.7% over 24 months
- March 2024 was the only negative-savings month (–$477) due to a double housing payment — flagged as an anomaly
- Transportation costs grew 17% YOY — largest category increase
- 42% of all spending used credit cards
- 274 flagged overspend transactions across 22 of 24 months

## Project Structure
| File | Description |
|------|-------------|
| `data/finance_transactions.csv` | 765-row synthetic dataset |
| `sql/finance_analysis.sql` | 8 analytical SQL queries |
| `python/finance_data_generation.py` | Data generation + 3 charts |
| `images/` | Chart exports and dashboard screenshots |

## SQL Skills Demonstrated
- GROUP BY, aggregations, CASE WHEN
- JOIN across multiple tables
- HAVING to filter aggregated results
- Window functions: SUM() OVER(), AVG() OVER(ROWS PRECEDING)
- CTEs for rolling averages

## Power BI Dashboard
[View live dashboard →](https://app.powerbi.com/your-link-here)](https://sooners-my.sharepoint.com/:u:/r/personal/jose_y_aguero-1_ou_edu/Documents/data%20portfolio/healthcare.pbix?csf=1&web=1&e=mYfOhw)

## How to Run the Python Script
```bash
pip install pandas numpy matplotlib
python python/finance_data_generation.py
```

HEALTHCARE — hospital-readmission-analysis/README.md
markdown# Hospital Patient Readmission Analysis

## Overview
End-to-end data analysis project examining 10,000 synthetic hospital patient records
to identify 30-day readmission risk factors across 8 departments and 8 primary diagnoses.

**Tools used:** Python · SQL (SQLite) · Power BI

## Key Findings
- Overall 30-day readmission rate of 20.4% across 10,000 patients
- Pulmonology had the highest readmission rate at 21.6% — above the hospital average
- Heart Failure was the highest-risk diagnosis at 22.0% readmission rate
- Patients with HbA1c >8 showed significantly higher readmission probability
- Average length of stay was 4.9 days
- 578 high-risk patients identified using an engineered risk score combining 8 clinical factors

## Project Structure
| File | Description |
|------|-------------|
| `data/healthcare_patients.csv` | 10,000-row synthetic patient dataset |
| `sql/healthcare_analysis.sql` | 8 analytical SQL queries |
| `python/healthcare_data_generation.py` | Data generation + 4 EDA charts |
| `images/` | Chart exports and Power BI dashboard screenshot |

## SQL Skills Demonstrated
- Aggregate functions with CAST for percentage calculations
- GROUP BY and HAVING for department-level filtering
- CASE WHEN for risk tier bucketing and length-of-stay grouping
- RANK() OVER() window function for department ranking
- COUNT() OVER() window function for percentage of total
- CTEs for multi-step risk segmentation analysis
- Multi-condition WHERE filtering for high-risk patient identification

## Power BI Dashboard
[View live dashboard →](https://app.powerbi.com/your-link-here)

![Dashboard preview](images/powerbi_dashboard.png)

## How to Run the Python Script
```bash
pip install pandas numpy matplotlib seaborn
python python/healthcare_data_generation.py
```
