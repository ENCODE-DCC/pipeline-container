cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: local_mapping

inputs:
  script_file:
    type: File
    inputBinding:
      position: 1

  reference_file:
    type: File
    inputBinding:
      position: 2

  trimming_length:
    type: string
    inputBinding:
      position: 3

  fastq_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 4

 
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
