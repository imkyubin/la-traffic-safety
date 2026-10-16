# Present this project in five minutes

Open **README → analysis.ipynb → Tableau**. The notebook follows the same four steps as this script.

## 0:00–0:30 — The question

“Our group used Los Angeles County crash records to understand when and where severe outcomes concentrate. We turned the raw records into a consistent analysis dataset, explored the patterns, evaluated one model, and communicated the findings in Tableau.”

## 0:30–1:45 — Cleaning decisions

Show section 1 of the notebook.

“We used one full-year snapshot containing 81,261 crashes from 2024–2025. Other files covered a shorter period, so we kept the input consistent. We retained 24 relevant fields and used CASE_ID to ensure that every row represented one crash.”

“We checked dates and parsed HHMM times, including invalid values such as 2500. We kept those 65 crashes in overall totals but excluded them from time-of-day comparisons. Missing coordinates only affected the map export. We defined severe as fatal or serious/severe injury and kept the denominator beside every rate.”

**Numbers to remember:** 81,261 total → 81,196 with valid time → 79,869 map-ready. Model eligibility is a separate filter: 81,182 records. There is no single blanket drop-missing-values step.

## 1:45–2:45 — EDA

Show the hourly chart and top-jurisdiction table in section 2.

“Counts and proportions answer different questions. Night had the largest number of severe crashes among our time blocks, while Late Night had the highest severe share. That share was 19.08%, compared with 7.75% at midday. Los Angeles, unincorporated areas, and Long Beach had the highest severe-crash counts.”

“These are shares among reported injury crashes, not the chance of crashing while driving. Traffic exposure is not in this dataset.”

## 2:45–3:45 — One model

Show the evaluation chart in section 3.

“We evaluated a random forest using earlier crashes for training and later crashes for testing. Balanced class weights addressed the minority severe class. We kept the original settings and evaluated at a fixed 0.50 threshold.”

“ROC AUC was about 0.627. Severe precision was 17% and recall was 32%, so the model's predictive value was modest. Accuracy alone would hide that: always predicting the majority class would be about 89% accurate while catching none of the severe cases. The strength of this step is explaining the split, class imbalance, and errors honestly.”

This predicts severity **given a recorded crash**. Features such as hit-and-run status are known afterward, so it cannot support advance deployment forecasting.

## 3:45–5:00 — Tableau and the takeaway

Open the [interactive hotspot map](https://public.tableau.com/app/profile/kyubin.im/viz/Book1_17766647170630/Sheet1).

“We made the observed patterns explorable in Tableau. Mark size shows crash count; color shows severe share. The controls let viewers compare time periods and other crash categories. I check the count behind a high percentage before interpreting a location.”

“The contribution is a reproducible path from messy records to an understandable decision-support dashboard. The findings help identify places and times for closer investigation; we did not measure the effect of a patrol intervention.”

**If asked about teamwork:** “All four of us contributed collaboratively across the project.”
