cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerPull: quay.io/gabdank/xcor:latest

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
  xcor_log:
    type: File
    outputBinding:
      glob: "xcor.log"
  cc_file:
    type: File
    outputBinding:
      glob: "*.cc.qc"
  cc_plot:
    type: File
    outputBinding:
      glob: "*.cc.plot.pdf"
  tag_align:
    type: File[]
    outputBinding:
      glob: "*.tagAlign.gz"