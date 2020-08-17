# serverless-aws-fec-data-collectionor
Serverless applications to get near-real-time FEC data

## About
All the serverless functions in this module do a few things:
- Gets values from SSM
- Use them to call the openFEC API
- Push that data to a queue or database
- Do so on a schedule or via event trigger

You can see the serverless functions defined in `serverless.yml` and the code in `src/`
The resources that support them are defined in CloudFormation in `prerequisite-cloudformation-resources.yml`.
The DDL is in the `sql/` directory.
The `bin/` has useful scripts that can be called via `make` targets defined in the `Makefile`.

### Functions
![](docs/data-flow-diagram.png)

### Entity Relationship Diagarm
![fec.png](docs/fec.png)

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
