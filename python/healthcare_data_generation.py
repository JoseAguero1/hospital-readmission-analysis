"""
Hospital Patient Readmission Analysis — Data Generation & EDA
=============================================================
Portfolio Project: Data Analyst Showcase
Author : Jose
Tools  : Python (pandas, numpy, matplotlib, seaborn)

Generates a 10,000-row synthetic hospital dataset and produces
4 publication-quality charts for Power BI / website portfolio.

Key dataset features:
  - 10,000 patients across 8 departments and 8 diagnoses
  - Realistic readmission probability driven by 8 risk factors
  - Missing values in race, hba1c_result, glucose_serum (~8%)
  - readmission_risk_score column engineered from risk factors

Outputs
-------
  healthcare_patients.csv              — clean dataset for SQL & Power BI
  hc_chart1_readmission_by_dept.png   — readmission rate by department
  hc_chart2_readmission_by_diagnosis.png — readmission by diagnosis
  hc_chart3_correlation_heatmap.png   — risk factor correlation heatmap
  hc_chart4_los_vs_readmission.png    — length of stay vs readmission rate
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

np.random.seed(42)
N = 10000

# ── REFERENCE DATA ────────────────────────────────────────────────────────
ages        = ['[0-10)','[10-20)','[20-30)','[30-40)','[40-50)',
               '[50-60)','[60-70)','[70-80)','[80-90)','[90-100)']
age_weights = [0.01,0.02,0.04,0.06,0.10,0.17,0.22,0.22,0.13,0.03]

races       = ['Caucasian','AfricanAmerican','Hispanic','Asian','Other']
race_w      = [0.55,0.25,0.10,0.05,0.05]

admission_types = ['Emergency','Urgent','Elective','Newborn','Trauma']
admit_w         = [0.40,0.25,0.25,0.05,0.05]

discharge_disp = ['Discharged to home','Transferred to SNF',
                  'Transferred to another hospital','Expired','Left AMA']
discharge_w    = [0.55,0.20,0.15,0.05,0.05]

admission_src  = ['Emergency Room','Physician Referral','Transfer from Hospital',
                  'Transfer from SNF','Court/Law Enforcement']
admit_src_w    = [0.40,0.35,0.15,0.08,0.02]

departments = ['Internal Medicine','Emergency/Trauma','Cardiology',
               'Orthopedics','Pulmonology','Nephrology','Neurology','Oncology']
dept_w      = [0.25,0.20,0.18,0.12,0.10,0.07,0.05,0.03]

primary_diags = ['Type 2 Diabetes','Heart Failure','Pneumonia','COPD',
                 'Hypertension','Renal Failure','Sepsis','Stroke']
diag_w        = [0.28,0.18,0.14,0.12,0.10,0.08,0.06,0.04]

# ════════════════════════════════════════════════════════════════════════
# STEP 1 — GENERATE DATASET
# ════════════════════════════════════════════════════════════════════════
df = pd.DataFrame({
    'patient_id':        [f'PT{100000+i}' for i in range(N)],
    'age':               np.random.choice(ages, N, p=age_weights),
    'gender':            np.random.choice(['Male','Female'], N),
    'race':              np.random.choice(races, N, p=race_w),
    'admission_type':    np.random.choice(admission_types, N, p=admit_w),
    'discharge_disposition': np.random.choice(discharge_disp, N, p=discharge_w),
    'admission_source':  np.random.choice(admission_src, N, p=admit_src_w),
    'department':        np.random.choice(departments, N, p=dept_w),
    'primary_diagnosis': np.random.choice(primary_diags, N, p=diag_w),
    'time_in_hospital':  np.random.choice(range(1,15), N,
                             p=[0.10,0.15,0.15,0.13,0.11,0.09,0.07,0.06,0.05,0.04,0.02,0.01,0.01,0.01]),
    'num_lab_procedures': np.random.randint(1, 70, N),
    'num_procedures':     np.random.randint(0, 7, N),
    'num_medications':    np.random.randint(1, 25, N),
    'num_diagnoses':      np.random.randint(1, 10, N),
    'num_outpatient_visits': np.random.poisson(0.4, N),
    'num_inpatient_visits':  np.random.poisson(0.3, N),
    'num_emergency_visits':  np.random.poisson(0.2, N),
    'insulin':            np.random.choice(['No','Steady','Up','Down'], N, p=[0.35,0.40,0.15,0.10]),
    'change_of_meds':     np.random.choice(['No','Ch'], N, p=[0.55,0.45]),
    'diabetes_med':       np.random.choice(['Yes','No'], N, p=[0.75,0.25]),
    'hba1c_result':       np.random.choice(['>8','>7','Normal','None'], N, p=[0.18,0.15,0.22,0.45]),
    'glucose_serum':      np.random.choice(['>300','>200','Normal','None'], N, p=[0.05,0.12,0.20,0.63]),
})

# Introduce ~8% missing values
for col in ['race','hba1c_result','glucose_serum']:
    mask = np.random.random(N) < 0.08
    df.loc[mask, col] = np.nan

# Readmission probability driven by risk factors
def calc_readmit(row):
    prob = 0.10
    if row['num_inpatient_visits'] > 1:             prob += 0.15
    if row['num_emergency_visits'] > 0:             prob += 0.10
    if row['hba1c_result'] == '>8':                 prob += 0.08
    if row['insulin'] in ['Up','Down']:             prob += 0.06
    if row['discharge_disposition'] == 'Transferred to SNF': prob += 0.07
    if row['admission_type'] == 'Emergency':        prob += 0.05
    if row['time_in_hospital'] > 7:                 prob += 0.05
    if row['num_diagnoses'] > 7:                    prob += 0.04
    return min(prob, 0.65)

probs = df.apply(calc_readmit, axis=1)
df['readmitted_30days']       = (np.random.random(N) < probs).astype(int)
df['readmission_risk_score']  = (probs * 100).round(1)

# Clean missing values
df['race']          = df['race'].fillna('Unknown')
df['hba1c_result']  = df['hba1c_result'].fillna('None')
df['glucose_serum'] = df['glucose_serum'].fillna('None')

df.to_csv('healthcare_patients.csv', index=False)
print(f"[1/5] Dataset saved: {len(df):,} rows, readmission rate {df['readmitted_30days'].mean()*100:.1f}%")

# ── PALETTE ───────────────────────────────────────────────────────────────
BLUE=    "#185FA5"; TEAL= "#1D9E75"; CORAL= "#D85A30"
GRAY_MID="#888780"; GRAY_DK="#2C2C2A"; BG="#FAFAF8"

plt.rcParams.update({
    "font.family":"DejaVu Sans","axes.facecolor":BG,"figure.facecolor":BG,
    "axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False,
    "axes.grid":True,"grid.color":"#E0DED6","grid.linewidth":0.5,
    "axes.labelcolor":GRAY_DK,"xtick.color":GRAY_MID,"ytick.color":GRAY_MID,"text.color":GRAY_DK,
})

# ════════════════════════════════════════════════════════════════════════
# STEP 2 — CHART 1: Readmission rate by department
# ════════════════════════════════════════════════════════════════════════
dept_readmit = (df.groupby('department')['readmitted_30days']
                .agg(['mean','count']).reset_index())
dept_readmit.columns = ['department','readmit_rate','patient_count']
dept_readmit['readmit_rate'] = (dept_readmit['readmit_rate']*100).round(1)
dept_readmit = dept_readmit.sort_values('readmit_rate', ascending=True)

fig, ax = plt.subplots(figsize=(10, 5.5))
avg = dept_readmit['readmit_rate'].mean()
colors = [CORAL if r > avg else TEAL for r in dept_readmit['readmit_rate']]
ax.barh(dept_readmit['department'], dept_readmit['readmit_rate'],
        color=colors, alpha=0.88, height=0.55, zorder=3)
ax.axvline(avg, color=BLUE, linewidth=1.5, linestyle='--', label=f'Avg ({avg:.1f}%)')
for i, (_, row) in enumerate(dept_readmit.iterrows()):
    ax.text(row['readmit_rate']+0.2, i, f"{row['readmit_rate']}%", va='center', fontsize=9)
ax.set_xlabel('30-Day Readmission Rate (%)'); ax.legend(fontsize=9, framealpha=0.85, edgecolor=GRAY_MID)
ax.set_title('30-Day Readmission Rate by Department', fontsize=13, fontweight='500', pad=14)
fig.tight_layout()
fig.savefig('hc_chart1_readmission_by_dept.png', dpi=160, bbox_inches='tight')
plt.close(); print("[2/5] Chart 1 saved")

# ════════════════════════════════════════════════════════════════════════
# STEP 3 — CHART 2: Readmission by diagnosis
# ════════════════════════════════════════════════════════════════════════
diag_readmit = (df.groupby('primary_diagnosis')['readmitted_30days']
                .mean().mul(100).round(1).reset_index()
                .sort_values('readmitted_30days', ascending=False))

fig, ax = plt.subplots(figsize=(10, 5))
bar_colors = [CORAL if i < 3 else TEAL for i in range(len(diag_readmit))]
ax.bar(diag_readmit['primary_diagnosis'], diag_readmit['readmitted_30days'],
       color=bar_colors, alpha=0.88, zorder=3)
ax.axhline(diag_readmit['readmitted_30days'].mean(), color=BLUE,
           linewidth=1.5, linestyle='--', label='Average')
for i, (_, row) in enumerate(diag_readmit.iterrows()):
    ax.text(i, row['readmitted_30days']+0.3, f"{row['readmitted_30days']}%", ha='center', fontsize=9)
plt.xticks(rotation=30, ha='right', fontsize=9)
ax.set_ylabel('Readmission Rate (%)'); ax.legend(fontsize=9, framealpha=0.85, edgecolor=GRAY_MID)
ax.set_title('30-Day Readmission Rate by Primary Diagnosis', fontsize=13, fontweight='500', pad=14)
fig.tight_layout()
fig.savefig('hc_chart2_readmission_by_diagnosis.png', dpi=160, bbox_inches='tight')
plt.close(); print("[3/5] Chart 2 saved")

# ════════════════════════════════════════════════════════════════════════
# STEP 4 — CHART 3: Correlation heatmap
# ════════════════════════════════════════════════════════════════════════
hba1c_map   = {'>8':3,'>7':2,'Normal':1,'None':0}
insulin_map = {'Up':3,'Down':2,'Steady':1,'No':0}
admit_map   = {'Emergency':4,'Trauma':3,'Urgent':2,'Elective':1,'Newborn':0}

corr_df = df[['readmitted_30days','time_in_hospital','num_medications',
              'num_diagnoses','num_inpatient_visits','num_emergency_visits',
              'num_lab_procedures','readmission_risk_score']].copy()
corr_df['hba1c_encoded']     = df['hba1c_result'].map(hba1c_map)
corr_df['insulin_encoded']   = df['insulin'].map(insulin_map)
corr_df['admission_encoded'] = df['admission_type'].map(admit_map)

fig, ax = plt.subplots(figsize=(11, 8))
mask = np.triu(np.ones_like(corr_df.corr(), dtype=bool))
sns.heatmap(corr_df.corr(), mask=mask, annot=True, fmt='.2f',
            cmap='RdYlGn', center=0, vmin=-1, vmax=1,
            ax=ax, linewidths=0.5, annot_kws={'size':9}, cbar_kws={'shrink':0.8})
ax.set_title('Correlation Heatmap — Readmission Risk Factors', fontsize=13, fontweight='500', pad=14)
plt.xticks(rotation=35, ha='right', fontsize=9); plt.yticks(fontsize=9)
fig.tight_layout()
fig.savefig('hc_chart3_correlation_heatmap.png', dpi=160, bbox_inches='tight')
plt.close(); print("[4/5] Chart 3 saved")

# ════════════════════════════════════════════════════════════════════════
# STEP 5 — CHART 4: Length of stay vs readmission
# ════════════════════════════════════════════════════════════════════════
los_readmit = df.groupby('time_in_hospital')['readmitted_30days'].mean().mul(100).round(1)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(los_readmit.index, los_readmit.values, color=CORAL,
        linewidth=2.2, marker='o', markersize=6, zorder=3)
ax.fill_between(los_readmit.index, los_readmit.values, alpha=0.12, color=CORAL)
for x, y in zip(los_readmit.index, los_readmit.values):
    ax.text(x, y+0.5, f'{y:.0f}%', ha='center', fontsize=8.5)
ax.set_xlabel('Length of Stay (days)'); ax.set_ylabel('Readmission Rate (%)')
ax.set_title('Readmission Rate by Length of Stay', fontsize=13, fontweight='500', pad=14)
ax.set_xticks(range(1,15))
fig.tight_layout()
fig.savefig('hc_chart4_los_vs_readmission.png', dpi=160, bbox_inches='tight')
plt.close(); print("[5/5] Chart 4 saved")
