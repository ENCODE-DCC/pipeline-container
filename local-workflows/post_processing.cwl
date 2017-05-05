cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: mapping

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

outputs:
  bam_output:
    type: File
    outputBinding:
      glob: "*.bam"
