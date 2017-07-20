dct:creator:
  "@id": "http://orcid.org/0000-0001-5025-5886"
  foaf:name: Idan Gabdank
  foaf:mbox: "mailto:gabdank@stanford.edu"

cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/gabdank/validator:0705.3

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