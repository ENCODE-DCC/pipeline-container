cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/gabdank/filter:latest

inputs:
  bam_file:
    type: File
    inputBinding:
      position: 1

outputs:
    filtered_bams:
        type: File[]
        outputBinding:
          glob: "*.bam"
    filtered_bam_bai:
        type: File
        outputBinding:
          glob: "*.bai"
    filtered_map_stats:
        type: File
        outputBinding:
          glob: "*.flagstat.qc"
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

