cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: DockerRequirement
    dockerImageId: xcor:latest

inputs:
  bam_file:
    type: File
    inputBinding:
      position: 1
  spp_1.10.1:
    type: File
    inputBinding:
      position: 2
  spp_1.14:
    type: File
    inputBinding:
      position: 3
  r_tools_directory:
    type: Directory
    inputBinding:
      position: 4 
  renviron:
    type: File
    inputBinding:
      position: 5
  fastq_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 6

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