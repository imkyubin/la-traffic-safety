# The data and six cleaning decisions

Data files are not published in this repository. The workflow expects `crashes_2024_2025.csv.gz` in this folder; it has **81,261 rows and 24 source fields**, projected from the supplied `Crashes_sorted.csv`. All original rows and selected values are retained; cleaning happens when the workflow runs. Pandas reads the compressed file directly.

| Decision | Reason | Implementation |
| --- | --- | --- |
| **Use one snapshot** | The selected file covers Jan 2024–Dec 2025; the other crash/party/victim extract stops in Sep 2025. | Use this snapshot throughout; do not mix extracts. |
| **Keep one row per crash** | A crash with several people must not be counted several times. | Preserve CASE_ID, require unique nonmissing IDs, and avoid unnecessary party/victim joins. |
| **Standardize fields** | Whitespace and blank values can conceal missing data. | Trim strings, mark blanks missing, validate dates, county, and severity codes. |
| **Validate time explicitly** | HHMM is not an ordinary number; 2500 means unknown and minutes cannot exceed 59. | Parse hours/minutes; exclude 65 invalid-time rows only from time-dependent steps. |
| **Handle missing coordinates locally** | Removing a crash from the map should not remove it from county totals. | Require valid longitude/latitude for the Tableau export; 1,334 rows lack usable coordinates. |
| **Define the target and denominator** | A high count and a high severity share mean different things. | Severe = codes 1 or 2; share = severe crashes / recorded injury crashes in the same group. |

**Populations:** 81,261 total; 81,196 valid-time; 79,869 Tableau export; 81,182 model-eligible. Coordinate and time exclusions overlap. The model additionally requires its original road/context fields to be present.

## Fields used

- **Identity and time:** CASE_ID, ACCIDENT_YEAR, COLLISION_DATE, COLLISION_TIME, DAY_OF_WEEK.
- **Outcome:** COLLISION_SEVERITY: 1 fatal; 2 serious/severe; 3 suspected minor/visible injury; 4 possible injury/complaint of pain.
- **Location:** COUNTY, CITY, PRIMARY_RD, SECONDARY_RD, POINT_X (longitude), POINT_Y (latitude).
- **Road and crash context:** INTERSECTION, STATE_HWY_IND, HIT_AND_RUN, CONTROL_DEVICE, TYPE_OF_COLLISION, PRIMARY_COLL_FACTOR, PCF_VIOL_CATEGORY.
- **Involvement indicators:** ALCOHOL_INVOLVED, PEDESTRIAN_ACCIDENT, BICYCLE_ACCIDENT, MOTORCYCLE_ACCIDENT, TRUCK_ACCIDENT. Source Y/blank becomes 1/0 in the Tableau export.

STATE_HWY_IND is Y/N; INTERSECTION is Y/N; CONTROL_DEVICE D means none; HIT_AND_RUN F means felony. Unknown codes remain in the data; the existing model's binary flags indicate only explicit matches. The model's “surface street” flag is a proxy for non-state-highway status.

**Tableau periods:** Late Night 00:00–04:59; Morning Rush 05:00–09:59; Midday 10:00–14:59; Evening Rush 15:00–18:59; Night 19:00–23:59. The original model retains separate overlapping flags: evening hours 17–21 and late-night hours 20–23 plus 00.

## Source and scope

California Highway Patrol SWITRS, accessed through **Transportation Injury Mapping System (TIMS), Safe Transportation Research and Education Center, University of California, Berkeley**. [TIMS](https://tims.berkeley.edu/) · [Source terms](https://tims.berkeley.edu/about.php#terms).

The supplied records contain injury/fatal crashes, excluding property-damage-only cases. Original extraction date and final/provisional status were not recorded. File dates do not prove reporting completeness. [manifest.json](manifest.json) records the source and bundled-file checksums.

To run directly on the original full file: `python run.py --data "path/to/Crashes_sorted.csv"`. The loader selects the same 24 fields. Use `manifest.json` checksums to confirm you have the same snapshot.
