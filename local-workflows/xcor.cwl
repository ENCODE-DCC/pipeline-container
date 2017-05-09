cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: local_xcor

inputs:
  script_file:
    type: File
    inputBinding:
      position: 1
  bam_file:
    type: File
    inputBinding:
      position: 2
  common_path:
    type: Directory
    inputBinding:
      position: 3

outputs:
    filtered_bam:
        type: File
        outputBinding:
          glob: "*.nodup.bam"