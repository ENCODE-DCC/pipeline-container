dct:creator:
  "@id": "http://orcid.org/0000-0001-5025-5886"
  foaf:name: Idan Gabdank
  foaf:mbox: "mailto:gabdank@stanford.edu"

cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/encode-dcc/post_mapping:v0.6
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 4092 #"the process requires at least 4G of RAM
    outdirMin: 512000
    tmpdirMin: 512000

inputs:
  
  trimming_length:
    type: string
    inputBinding:
      position: 1
  
  reference_file:
    type: File
    inputBinding:
      position: 2
  
  unmapped_fastqs:
    type: File[]
    inputBinding:
      position: 3
  
  sai_files:
    type: File[]
    inputBinding:
      position: 4
  
  initial_fastqs:
    type: File[]
    inputBinding:
      position: 5

outputs:
  
  unfiltered_bam:
    type: File
    outputBinding:
      glob: "*.raw.srt.bam"
  
  unfiltered_flagstats:
    type: File
    outputBinding:
      glob: "*.raw.srt.bam.flagstat.qc"
  
  post_mapping_log:
    type: File
    outputBinding:
      glob: "post_mapping.log"  
  
  output_json:
    type: File
    outputBinding:
      glob: "post_mapping.json"

baseCommand: []