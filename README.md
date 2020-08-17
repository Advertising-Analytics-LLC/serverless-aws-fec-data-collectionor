# serverless-aws-fec-data-collectionor
Serverless applications to get near-real-time FEC data

## About
All the serverless functions in this module do a few things:
- Gets values from SSM
- Use them to call the openFEC API
- Push that data to a queue or database
- Do so on a schedule or via event trigger

### Repo Contents

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

You can see the serverless functions defined in `serverless.yml` and the code in `src/`
The resources that support them are defined in CloudFormation in `prerequisite-cloudformation-resources.yml`.
The DDL is in the `sql/` directory.
The `bin/` has useful scripts that can be called via `make` targets defined in the `Makefile`.

### Functions
The data-flow diagram below shows events, lambdas, queues, and RDS tables. Most data originates with the [FEC API](https://api.open.fec.gov/developers/) but also uses [fecfile](https://github.com/esonderegger/fecfile) to parse FEC filings from `https://docquery.fec.gov/paper/posted/{fec_file_id}.fec`

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

![](docs/fec.png)

## Getting started

### 0. Install prerequisites
Make sure [python](https://www.python.org/), [npm](https://www.npmjs.com/), and the [aws cli](https://aws.amazon.com/cli/) are installed.
The services are written in python and [serverless](https://www.serverless.com/) is an npm package. They are deployed to AWS.

### 1. Install development packages
These requirements can be installed with `bin/dev-setup.sh`.
This script installs serverless and creates a local python [virtualenv](https://virtualenv.pypa.io/en/latest/) for developing the functions.
See [bin/dev-setup.sh](bin/dev-setup.sh)

### 2. Develop
Edit the code and run locally with `sls invoke local -f hello`.
Replace `hello` with the name of your function.

### 3. Deploy
First you will need to log into AWS through the cli.
Then you can deploy your function with `sls deploy`.
Happy coding!


## References
If you want to see more let me suggest
- [the AWS serverless.yml reference](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/)
- this [serverless/examples example](https://github.com/serverless/examples/tree/master/aws-python-rest-api-with-pynamodb)
- [FEC API docs](https://api.open.fec.gov/developers/)
