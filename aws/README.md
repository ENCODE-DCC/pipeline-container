## Add AWS credentials to workflow file

#### Create workflow.yml

```
cp sample_workflow.yml workflow.yml
```

Edit workflow.yml with your AWS credentials, leaving the region untouched.
If you are naming the workflow.yml to something else, make sure to include it in .gitignore 
so as to not share your credentials with the internetz.

## Log your docker client into AWS (needed only once)
```
aws ecr get-login --region us-east-1
```
Copy the output of the above and paste it into command line. This is only temporary and won't be needed after orchestrating contanier is migrated from aws to quay.io

## Run with dockstore
```
dockstore tool launch --local-entry filter_qc.cwl --yaml workflow.yml --script
```