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
  trimming_length:
    type: string
    inputBinding:
      position: 2
  reference_file:
    type: File
    inputBinding:
      position: 3
  common_path:
    type: Directory
    inputBinding:
      position: 4
  unmapped_fastqs:
    type: File[]
    inputBinding:
      position: 5
  sai_files:
    type: File[]
    inputBinding:
      position: 6


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
