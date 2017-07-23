dct:creator:
  "@id": "http://orcid.org/0000-0001-5025-5886"
  foaf:name: Idan Gabdank
  foaf:mbox: "mailto:gabdank@stanford.edu"

cwlVersion: v1.0

class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/encode-dcc/filter:v0.4
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
  filtered_bam:
      type: File
      outputBinding:
        glob: "*final.bam"
  filtered_bam_bai:
      type: File
      outputBinding:
        glob: "*final.bam.bai"
  filtered_map_stats:
      type: File
      outputBinding:
        glob: "*final.flagstat.qc"
  dup_file_qc:
      type: File
      outputBinding:
        glob: "*.dup.qc"
  pbc_file_qc:
      type: File
      outputBinding:
        glob: "*.pbc.qc"
  filter_qc_log:
      type: File
      outputBinding:
        glob: "filter_qc.log"    
  output_json:
    type: File
    outputBinding:
      glob: "filter_qc.json"

baseCommand: []
