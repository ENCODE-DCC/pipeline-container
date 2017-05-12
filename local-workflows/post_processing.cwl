cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: post_mapping:latest

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
