cwlVersion: v1.0

class: Workflow

inputs:
  - id: script1
    type: File

  - id: script2
    type: File

  - id: fastq
    type: File

  - id: reference
    type: File


outputs:
  sai:
    type: File
    outputSource: mapper/sai_file
  bam:
    type: File
    outputSource: post_processing/bam_output
  cropped:
    type: File
    outputSource: mapper/cropped_file


steps:
  mapper:
    run: mapping.cwl
    in:
      script_file: script1
      fastq_file: fastq
      reference_file: reference
    out: [cropped_file, sai_file]

  post_processing:
    run: post_processing.cwl
    in:
      script_file: script2
      sai_file: mapper/sai_file
      cropped_fastq_file: mapper/cropped_file
      reference_file: reference
    out: [bam_output]