# Data

## Data Flow

The data-flow diagram below shows events, lambdas, queues, and RDS tables. Most data originates with the [FEC API](https://api.open.fec.gov/developers/) but also uses [fecfile](https://github.com/esonderegger/fecfile) to parse FEC filings from `https://docquery.fec.gov/paper/posted/{fec_file_id}.fec`.
You can also view the lambdas, along with monitoring and logging, through the [aws console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/applications/serverless-aws-python3-fec-datasync-dev?tab=overview)./

### Data-Flow Diagram

![](data-flow-diagram.png)

## Data Model

The tables came from:
- The [FEC API](https://api.open.fec.gov/developers/)
    - `candidate_detail` -> `CandidateDetail` from https://api.open.fec.gov/developers/#/candidate/get_candidate__candidate_id__
    - `committee_detail` -> `CommitteeDetail` from https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
    - `committee_candidates` -> `CommitteeDetail`
- The [docquery filings](https://docquery.fec.gov/paper/)
    - `filings`
    - `filings_amendment_chain`
    - `filings_schedule_b`
    - `filings_schedule_e`
    - `form_1_supplemental`
    - `committee_totals`

If you inspect the data-flow-diagram above you can see what API was used to make any redshift table.
Each API endpoint returns a different Data Model. The APIs and their DMs are listed above.
The `docquery` API returns fec files which are pretty free-form

### Entity Relationship Diagarm

This was generated using DataGrip and makes uses of the foreign keys which
[are not enforced by redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-defining-constraints.html)

![](fec.png)


## Database Statistics

There is an extra lambda, `GetDBStats`, that queries the database for row counts and the like.
It then writes this information back to the DB with a date for point-in-time records.
The lambda code is in `src/get_db_stats.py` and you can query for it's results from the database with `select * from fec.loading_stats;` to get something like this: 

| query\_time | candidate\_detail\_count | candidate\_detail\_min\_first\_file | committee\_detail\_count | committee\_detail\_min\_first\_file | filings\_count | filings\_min\_receipt\_date | committee\_totals\_count | filing\_amendment\_chain\_count | filings\_schedule\_b\_count | filings\_schedule\_e\_count | form\_1\_supplemental\_count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2020-08-21 15:40:48.731069 | 1166 | 2016-11-06 | 880 | 1972-06-09 | 11454 | 2019-01-20 | 897 | 0 | 18600 | 1951 | 0 |
| 2020-08-21 15:42:21.751421 | 1166 | 2016-11-06 | 880 | 1972-06-09 | 11454 | 2019-01-20 | 897 | 0 | 18600 | 1951 | 0 |
