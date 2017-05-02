## Add AWS credentials to workflow file

#### Create workflow.yml

```
cp sample_workflow.yml workflow.yml
```

Edit workflow.yml with your AWS credentials, leaving the region untouched.
If you are naming the workflow.yml to something else, make sure to include it in .gitignore 
so as to not share your credentials with the internetz.

## Run with dockstore
```
dockstore tool launch --local-entry filter_qc.cwl --yaml workflow.yml --script
```