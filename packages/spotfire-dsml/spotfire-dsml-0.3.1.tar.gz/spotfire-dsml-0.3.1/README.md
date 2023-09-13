[![Build](https://github.com/tibco/dsml-data-functions/actions/workflows/build.yml/badge.svg)](https://github.com/tibco/dsml-data-functions/actions/workflows/build.yml)

[![Build](https://github.com/tibco/dsml-data-functions/actions/workflows/release.yml/badge.svg)](https://github.com/tibco/dsml-data-functions/actions/workflows/release.yml)

# DSML Data Functions 

The DSML library is a collection of functions and machine learning models implemented in Python, that can be used as a service in various AI enabled applications.

This library contains reusable AI components that enables intelligence across various TIBCO products. These components are delivered as both Python packages and RESTful APIs. It also aims to make the implementation and maintenance of data functions easier, and helps the developers in tedious tasks by automating the end-to-end process using CI/CD. 

The project helps setting up all the various files, the virtual environment, and keeping things uniform across all functions. 

## Prerequisites

Before using the project, please make sure you have installed the prerequisites for your specific OS.  The links below provide a summary for Mac, Linux and Windows machines.

- [Mac](https://github.com/tibco/dsml-data-functions/blob/develop/Prerequisite_Mac.md)
- [Linux](https://github.com/tibco/dsml-data-functions/blob/develop/Prerequisite_Linux.md)
- [Windows](https://github.com/tibco/dsml-data-functions/blob/develop/Prerequisite_Win.md)


## Project Setup 

### Linux

```bash
# Create Virtual environment
make setvenv

# Switch to virtual enviroment
source ./venv/bin/activate

# Install required libraries
make install

# To deactivate virtual environemnt
deactivate
```


### Windows

```bash
# Create Virtual environment
make -f Makefile_WIN setvenv

# Switch to virtual enviroment
venv\Scripts\activate.bat

# Install required libraries
make -f Makefile_WIN install

# To deactivate virtual environemnt
deactivate
```

## To use DSML Data Functions Python library
 - ### By importing as modules 

    1. Configure AWS to access DSML AWS resources from CLI.  See [AWS CLI configuration](#AWS-CLI-Configuration).
    2. Login to AWS Code Artifact repository.  The login fetches an authorization token from CodeArtifact using your AWS credentials and  configure pip for use with CodeArtifact. The default authorization period after calling login is 12 hours, and login must be called to periodically refresh the token.
        ```bash
        aws codeartifact login --profile dsml-user --tool pip --repository dsml-datafunctions-repository --domain tibco-dsml --domain-owner 132114974369 --region us-east-1
        ```
    2. Install library
        ```bash
        pip install tibco-dsml
        ```
    3. Import specific library module.<br>
      For example:
        ```bash
        from dsmllib.exploration import column_correlation
        ```
  
## To use DSML Data Functions REST Interface 

- ### Using deployed service

    1. Get Library URL
    2. Call desired function. For example:
        ```bash
        curl -X 'POST' \
        'http://127.0.0.1:8000/exploration/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
          ...
          ...
        }'
        ```

- ### Using docker image build locally

    1. Set and install environment as indicate in Project Setup
    2. Build docker image
        ```bash
        make build-image
        ```
    3. Run docker image
        ```bash
        make run
        ```
    4. Now you can use the URL returned in the previous step to call the functions. For example:
        ```bash
        curl -X 'POST' \
        'http://localhost:8000/exploration/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
          ...
          ...
        }'
        ```
- ### Using docker image pulled from AWS Container Registry

    1. Configure AWS to access DSML AWS resources.  See [AWS CLI configuration](#AWS-CLI-Configuration).
    2. Login to AWS Elastic Container Registry (ECR)
        ```bash
        aws ecr get-login-password --profile dsml-user --region us-east-1 | docker login --username AWS --password-stdin 132114974369.dkr.ecr.us-east-1.amazonaws.com
        ```
    3. Pull docker image from AWS ECR
        ```bash
        docker pull 132114974369.dkr.ecr.us-east-1.amazonaws.com/dsml-data-functions:latest
        ```
    4. Run docker image
        ```bash
        docker run -p 127.0.0.1:8080:8080 132114974369.dkr.ecr.us-east-1.amazonaws.com/dsml-data-functions:latest
        ```
    5. Now you can use the URL returned in the previous step to call the functions. For example:
        ```bash
        curl -X 'POST' \
        'http://localhost:8000/exploration/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
          ...
          ...
        }'
        ```

##
- [To run the examples](https://github.com/tibco/dsml-data-functions/blob/wf_megha/examples/)
- [To create or update Data Functions](https://github.com/tibco/dsml-data-functions/blob/wf_megha/dsmllib/)

## Document generation

- ### To generate HTML documentation for all data functions
```bash
  make doc-generate-html
```
## AWS CLI Configuration

In order to get DSML resources from AWS, a user must have the permissions to access those resources.   If user trying to use DSML resources has only "View" access to the DSML AWS account, the following steps need to be completed:

- ### Configure AWS .aws/credentials file
  Configure the credentials file with the credentails obtained from the AWS Portal Page.  For example:
  ```bash
  [132114974369_view]
  aws_access_key_id=CHANGE_ME
  aws_secret_access_key=CHANGE_ME
  aws_session_token=CHANGE_ME
  ```
- ### Configure AWS profile file .aws/config to add a role with permissions to access the DSML resources. For example: 
  ```bash
  [profile dsml-user]
  region = us-east-1
  output = json
  role_arn = arn:aws:iam::132114974369:role/DSMLCodeArtifactAccessRole
  source_profile=132114974369_view  
  ```

Please note that the dsml-user profile will be used in AWS commands requiring the DSMLResourcesAccessRole
