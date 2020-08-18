# Engineering

## Getting started

These instructions are for engineers wishing to develop the project.

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
