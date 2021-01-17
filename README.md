## Architectural decisions

## Challenge 1

![arch diagram](aiq-challenge.png)

- The solution is based on a AWS cloud platform.
- The following principles were used:
    - use data lake approach instead of DWH
    - abstract raw data via Data Marts
    - implement data processing in a manual batch mode
- Data versioning, data lineage, metadata service weren't implemented due to time limits of the challenge.
- Since the data volume is small no distributed data processing was used.
- Since the data transformation worklow is simple, single serverless function was used. In case the complexity will increase, the solution should be replaced by a proper worklow manager (Apache Airflow, AWS Step Function, etc.).
- Infrastructure is managed via `Ansible` and `make` tools. `make` builds lambda layer and function and orchestrates overall workflow. `Ansible` builds most of the AWS infrastructure.
- Push based configuration approach.
- FastAPI Python framework on EC2 instance is used for Web service.
- To increase performance the data is cached locally on a web server FS. Since the data is uncheangable, no cache invalidation is needed. But cache eviction must be implemented.

## Challenge 2

- DynamoDB was used as a database of choice, mainly because data query use cases were simple and it is easy to setup. It's generally not suited for OLAP activities, but for this scenario it might be well suited, perfomance and pricing testing need to be conducted.

## Runbook

### Prerequisites

- `jq` and `zip` tools installed locally
- `docker` installed locally
- `python` 3.7+ and `pip` installed locally
- AWS account with programmatic access (key and secret key)
- SSH puplic key is uploaded to AWS EC2 console

### Setup

### Challenge 1 

- run: `cd challenge-1 && make init` - if AWS account wasn't set up it will ask you interactivelly
- modify `infrastructure/config.yml` file:
    - change name to your uploaded SSH key name (`aws_ssh_key`)
    - change path to raw test example data: `test_data_file` (not necessary for challenge 1)
- run: `make`
- wait for complete and follow the instructions how to test APIs

make command will:
- build necessary infrastructure
- upload raw data to S3 storage
- run preprocessing AWS lambda job synchronously
- run the web service
- print the instructions how to test APIs and check their specification

### Challenge 2

the steps are the same as for challenge 1.
