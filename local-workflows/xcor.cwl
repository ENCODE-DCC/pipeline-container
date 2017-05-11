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
  paired:
    type: boolean
    inputBinding:
      position: 3
  common_path:
    type: Directory
    inputBinding:
      position: 4
  spp_1.10.1:
    type: File
    inputBinding:
      position: 5
  spp_1.14:
    type: File
    inputBinding:
      position: 6
  r_tools_directory:
    type: Directory
    inputBinding:
      position: 7 
  renviron:
    type: File
    inputBinding:
      position: 8
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