# Tableau hotspot map

**[Open the interactive dashboard](https://public.tableau.com/app/profile/kyubin.im/viz/Book1_17766647170630/Sheet1)**

[![Original Tableau hotspot map](preview.png)](https://public.tableau.com/app/profile/kyubin.im/viz/Book1_17766647170630/Sheet1)

## What to demonstrate

1. Explain the marks: **size = recorded crash count; color = severe share**.
2. Use the available time-period/category controls to compare Night, Late Night, and Midday.
3. Hover over a location and inspect its count before interpreting a high percentage.

The map groups coordinates rounded to two decimals. Its measures are `COUNT([collision_severity_binary])` and `AVG([collision_severity_binary])`. It displays observed crashes and proportions; no model predictions are used.

## Connect the Python workflow

`python run.py` creates `outputs/tableau_proportional_severity_data.csv`: **79,869 records**, using the original 17-column export schema. Download the workbook from Tableau Public and point a local working copy's data connection to this CSV to refresh it. The packaged workbook is not stored here because it embeds a data extract.

The published workbook keeps its embedded Hyper extract. Its counts can differ from the refreshed export: the cleaned workflow preserves crash IDs and avoids dropping records for an unused tow-away field. The live dashboard is not changed by running Python.

Workbook and preview retrieved from the public project on 2026-10-15; [provenance and checksum](../data/manifest.json). Package integrity and embedded extract paths were verified. Local Tableau Desktop refresh was not tested. Original basemap credits remain intact.
