dct:creator:
  "@id": "http://orcid.org/0000-0001-5025-5886"
  foaf:name: Idan Gabdank
  foaf:mbox: "mailto:gabdank@stanford.edu"

cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/encode-dcc/mapping
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 4092 #"the process requires at least 4G of RAM
    outdirMin: 512000
    tmpdirMin: 512000

inputs:

  reference_file:
    type: File
    inputBinding:
      position: 1

  trimming_length:
    type: string
    inputBinding:
      position: 2

  fastq_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 3

 
outputs:
  unmapped_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.gz"

  sai_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.sai"
  
  mapping_log:
    type: File
    outputBinding:
      glob: "mapping.log"

baseCommand: []