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

