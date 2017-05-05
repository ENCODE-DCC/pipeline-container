cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: local_post_processing

inputs:
  script_file:
    type: File
    inputBinding:
      position: 1
  sai_file:
    type: File
    inputBinding:
      position: 2
  cropped_fastq_file:
    type: File
    inputBinding:
      position: 3
  reference_file:
    type: File
    inputBinding:
      position: 4
  common_path:
    type: Directory
    inputBinding:
      position: 5

outputs:
  bam_output:
    type: File
    outputBinding:
      glob: "*.bam"
  post_mapping_log:
      type: File
      outputBinding:
        glob: "*.log"  
