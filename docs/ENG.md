# Engineering

## Getting started

These instructions are for engineers wishing to develop the project.

### 0. Install prerequisites
Make sure [python](https://www.python.org/), [terraform](https://www.terraform.io/), [docker](https://www.docker.com/), and the [aws cli](https://aws.amazon.com/cli/) are installed.
The services are written in python and deployed to AWS using Terraform.

### 1. Install development packages
Pyenv is used for python versioning. 
```sh
# install python version
pyenv install

# create virtualenv
python3 -m venv .venv

# activate virtualenv
source .venv/bin/activate

# install python dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

### 2. AWS Authentication

The Terraform configuration uses a remote S3 backend and assumes a role in the target account.

**Backend Setup:**
- Terraform state is stored in S3 bucket: `767398000173-us-east-1-tfstate-product`
- State locking uses DynamoDB table: `tf-locktable-product`
- You must be authenticated to AWS account `767398000173` to run Terraform

**Assume Role:**
- Terraform assumes role `arn:aws:iam::648881544937:role/Terraform` in the target account
- Resources are created in account `648881544937`


### 3. Terraform Setup

Navigate to the infrastructure directory:
```sh
cd infrastructure
```

Initialize Terraform (this will configure the remote backend):
```sh
make init
```

### 4. Configure Variables

Edit `terraform.tfvars` to set your desired values (see `docs/TERRAFORM.md` for details).

### 5. Develop

Edit the code in `lambdas/src/` and test locally. You can test Lambda functions locally using tools like [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) or by running the Python code directly.

### 6. Deploy

Review changes:
```sh
make plan
```

Apply changes:
```sh
make apply
```

For automated deployments:
```sh
make autoapply
```

### 7. Make Targets

The `infrastructure/Makefile` provides convenient targets:
- `make init` - Initialize Terraform
- `make plan` - Show planned changes
- `make apply` - Apply changes (interactive)
- `make autoapply` - Apply changes (non-interactive)
- `make destroy` - Destroy infrastructure
- `make output` - Show Terraform outputs
