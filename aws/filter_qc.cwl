cwlVersion: v1.0
class: CommandLineTool
baseCommand: [aegea, batch, submit]
arguments: ["--image", "quay.io/gabdank/filter_qc:latest", "--command", "python /tmp/pipeline-container/containers/filter_qc/src/filter_qc.py", "--memory", $(inputs.compute_environment.memory), "--vcpus", $(inputs.compute_environment.vcpus), "--watch"]
requirements:
    EnvVarRequirement:
        envDef: 
            AWS_ACCESS_KEY_ID: $(inputs.aws_credentials.access_key_id)
            AWS_SECRET_ACCESS_KEY: $(inputs.aws_credentials.secret_access_key)
            AWS_DEFAULT_REGION: $(inputs.aws_credentials.default_region)
    DockerRequirement:
        dockerPull: 618537831167.dkr.ecr.us-east-1.amazonaws.com/encode_aws_pipeline
inputs: [] 
outputs: []