dct:creator:
  "@id": "http://orcid.org/0000-0001-5025-5886"
  foaf:name: Idan Gabdank
  foaf:mbox: "mailto:gabdank@stanford.edu"

cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/jseth/xcor:summary_outputs
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 4092 #"the process requires at least 4G of RAM
    outdirMin: 512000
    tmpdirMin: 512000

inputs:
  bam_file:
    type: File
    inputBinding:
      position: 1
  fastq_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 2

outputs:
  xcor_log:
    type: File
    outputBinding:
      glob: "xcor.log"
  cc_file:
    type: File
    outputBinding:
      glob: "*.cc.qc"
  cc_plot:
    type: File
    outputBinding:
      glob: "*.cc.plot.pdf"
  tag_align:
    type: File[]
    outputBinding:
      glob: "*tagAlign.gz"
  output_json:
    type: File
    outputBinding:
      glob: "xcor.json"

baseCommand: []