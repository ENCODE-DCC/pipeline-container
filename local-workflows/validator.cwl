cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/encode-dcc/validator:v1.0

inputs:

  output_folder:
    type: Directory
    inputBinding:
      position: 1


outputs:
  results_file:
    type: File
    outputBinding:
      glob: results.json
    doc: A json file that contains the result of the test

baseCommand: []
