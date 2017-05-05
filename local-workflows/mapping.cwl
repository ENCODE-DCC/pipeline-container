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
  fastq_file:
    type: File
    inputBinding:
      position: 2
  reference_file:
    type: File
    inputBinding:
      position: 3

outputs:
    cropped_file:
        type: File
        outputBinding:
          glob: "*.-crop.fq.gz"
    sai_file:
        type: File
        outputBinding:
          glob: "*.-crop.sai"    

