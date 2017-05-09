cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: local_filter_qc

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
          glob: "*.raw.srt.filt.srt.bam"
    filtered_bam_bai:
        type: File
        outputBinding:
          glob: "*.filt.nodup.srt.bam.bai"
    filtered_map_stats:
        type: File
        outputBinding:
          glob: "*.raw.srt.filt.nodup.srt.flagstat.qc"
    dup_file_qc:
        type: File
        outputBinding:
          glob: "*.raw.srt.dup.qc"
    pbc_file_qc:
        type: File
        outputBinding:
          glob: "*.nodup.srt.pbc.qc"
    filter_qc_log:
        type: File
        outputBinding:
         glob: "filter_qc.log"    

