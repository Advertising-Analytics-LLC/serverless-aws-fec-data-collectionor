# serverless-aws-fec-data-collectionor
Serverless applications to get near-real-time FEC data

## Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [About](#about)
  - [Repo Contents](#repo-contents)

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
