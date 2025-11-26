# serverless-aws-fec-data-collectionor
Terraform-managed AWS infrastructure to get near-real-time FEC data by scraping the FEC APIs using Lambda and storing the data in RedShift

## About
All the Lambda functions in this module do a few things:
- Get secrets/variables from SSM
- Call the openFEC API
- Push data to a queue or database
- Do so on a schedule or via event trigger

## Documentation

View it live on GitHub Pages: https://advertising-analytics-llc.github.io/serverless-aws-fec-data-collectionor/

- `docs/ENG.md` has the Engineering stuff (including Terraform setup)
- `docs/OPS.md` has the Operations stuff
- `docs/DATA.md` has the data models
- `docs/TERRAFORM.md` has Terraform-specific documentation

## Repo Contents

The infrastructure is defined in Terraform in the `infrastructure/` directory.
The Lambda function code is in `lambdas/src/`.
The resources that support them are defined in CloudFormation in `infrastructure/prerequisite-cloudformation-resources.yml`.
The DDL is in the `sql/` directory.
The `bin/` has useful scripts that can be called via `make` targets defined in the `Makefile`.

```sh
.
├── Makefile
├── README.md
├── bin                     # scripts
├── dev-requirements.txt    # requirements for developing code
├── docs                    # documentation source
├── infrastructure          # Terraform configuration
│   ├── main.tf            # main Terraform configuration
│   ├── Makefile           # Terraform make targets
│   └── terraform.tfvars   # variable values
├── lambdas                # Lambda function code
│   └── src                # Python source code
├── requirements.txt        # requirements for running code
└── sql                    # SQL DDL
```
