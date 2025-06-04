# serverless-aws-fec-data-collectionor
Serverless applications to get near-real-time FEC data

## About
All the serverless functions in this module do a few things:
- Get secrets/variables from SSM
- Call the openFEC API
- Push data to a queue or database
- Do so on a schedule or via event trigger

## Documentation

View it live on GitHub Pages: https://advertising-analytics-llc.github.io/serverless-aws-fec-data-collectionor/

- `docs/ENG.md` has the Engineering stuff
- `docs/OPS.md` has the Operations stuff
- `docs/DATA.md` has the data models

## Repo Contents

You can see the serverless functions defined in `serverless.yml` and the code in `src/`
The resources that support them are defined in CloudFormation in `prerequisite-cloudformation-resources.yml`.
The DDL is in the `sql/` directory.
The `bin/` has useful scripts that can be called via `make` targets defined in the `Makefile`.

```sh
.
├── Makefile
├── README.md
├── bin                     # scripts
├── dev-requirements.txt    # requirements for developing code
├── docs                    # documentation source
├── package.json
├── prerequisite-cloudformation-resources.yml # SQS qs, SNS topics, S3 Bucket
├── requirements.txt    # requirements for running code
├── serverless.yml      # serverless function definitions
├── sql                 # SQL DDL
├── src                 # python code
```
