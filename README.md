# serverless-aws-fec-data-collectionor
Serverless applications to get near-real-time FEC data

## Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [About](#about)
  - [Repo Contents](#repo-contents)
  - [Functions](#functions)
    - [Data-Flow Diagram](#data-flow-diagram)
  - [Data Model](#data-model)
    - [Entity Relationship Diagarm](#entity-relationship-diagarm)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## About
All the serverless functions in this module do a few things:
- Get secrets/variables from SSM
- Call the openFEC API
- Push data to a queue or database
- Do so on a schedule or via event trigger

### Repo Contents

You can see the serverless functions defined in `serverless.yml` and the code in `src/`
The resources that support them are defined in CloudFormation in `prerequisite-cloudformation-resources.yml`.
The DDL is in the `sql/` directory.
The `bin/` has useful scripts that can be called via `make` targets defined in the `Makefile`.

```
.
├── Makefile
├── README.md
├── bin
├── dev-requirements.txt
├── docs
├── node_modules
├── package-lock.json
├── package.json
├── prerequisite-cloudformation-resources.yml
├── requirements.txt
├── serverless.yml
├── sql
├── src
├── tests
└── tmp
```

### Functions
The data-flow diagram below shows events, lambdas, queues, and RDS tables. Most data originates with the [FEC API](https://api.open.fec.gov/developers/) but also uses [fecfile](https://github.com/esonderegger/fecfile) to parse FEC filings from `https://docquery.fec.gov/paper/posted/{fec_file_id}.fec`.
You can also view the lambdas, along with monitoring and logging, through the [aws console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/applications/serverless-aws-python3-fec-datasync-dev?tab=overview)./

#### Data-Flow Diagram

![](docs/data-flow-diagram.png)

### Data Model

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

#### Entity Relationship Diagarm

This was generated using DataGrip and makes uses of the foreign keys which
[are not enforced by redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-defining-constraints.html)

![](docs/fec.png)


## References
Resources I referenced when making design decisions

- [the AWS serverless.yml reference](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/)
- this [serverless/examples example](https://github.com/serverless/examples/tree/master/aws-python-rest-api-with-pynamodb)
- [FEC API docs](https://api.open.fec.gov/developers/)
