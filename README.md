# serverless-aws-python3-openfec-starter
Reference serverless project

## About
This is a reference serverless project that does a few simple things:
- Gets an API key from SSM
- Uses key to call OpenFEC API `/dates/election-dates`
- Pulls the most recent general election

it does this on a schedule powered by CloudWatch Events

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
