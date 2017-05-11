cwlVersion: v1.0

class: Workflow

inputs:
  - id: script1
    type: File

  - id: script2
    type: File

  - id: script3
    type: File

  - id: script4
    type: File

  - id: trimming_parameter
    type: string

  - id: fastqs
    type: File[]

  - id: reference
    type: File

  - id: common
    type: Directory

  - id: spp_1.10.1
    type: File
  
  - id: spp_1.14
    type: File

  - id: r_tools_directory
    type: Directory

  - id: renviron
    type: File

  - id: paired
    type: boolean


outputs:
#  sais:
#    type: File[]
#    outputSource: mapper/sai_files
  unfiltered_bam:
    type: File
    outputSource: post_processing/unfiltered_bam
  filtered_bam:
    type: File
    outputSource: filter_qc/filtered_bam
  unfiltered_flagstat:
    type: File
    outputSource: post_processing/unfiltered_flagstats
  filtered_flagstat:
    type: File
    outputSource: filter_qc/filtered_map_stats
  dup_qc:
    type: File
    outputSource: filter_qc/dup_file_qc
  pbc_qc:
    type: File
    outputSource: filter_qc/pbc_file_qc
  mapping_log:
    type: File
    outputSource: mapper/mapping_log
  post_mapping_log:
    type: File
    outputSource: post_processing/post_mapping_log
  filter_qc_log:
    type: File
    outputSource: filter_qc/filter_qc_log
  xcor_log:
    type: File
    outputSource: xcor/xcor_log
  cc:
    type: File
    outputSource: xcor/cc_file
  cc_pdf:
    type: File
    outputSource: xcor/cc_plot
  tag_align:
    type: File[]
    outputSource: xcor/tag_align


steps:

  mapper:
    run: mapping.cwl
    in:
      script_file: script1
      reference_file: reference
      trimming_length: trimming_parameter
      fastq_files: fastqs
    out: [unmapped_files, sai_files, mapping_log]

  post_processing:
    run: post_processing.cwl
    in:
      script_file: script2
      trimming_length: trimming_parameter
      reference_file: reference
      common_path: common
      unmapped_fastqs: mapper/unmapped_files
      sai_files: mapper/sai_files
    out: [unfiltered_bam, unfiltered_flagstats, post_mapping_log]

  filter_qc:
    run: filter_qc.cwl
    in:
      script_file: script3
      bam_file: post_processing/unfiltered_bam
      common_path: common
    out: [filtered_bam, filtered_bam_bai, filtered_map_stats, dup_file_qc, pbc_file_qc, filter_qc_log]

  xcor:
    run: xcor.cwl
    in:
      script_file: script4
      bam_file: filter_qc/filtered_bam
      paired: paired
      common_path: common
      spp_1.10.1: spp_1.10.1
      spp_1.14: spp_1.14
      r_tools_directory: r_tools_directory
      renviron: renviron
    out: [cc_file, cc_plot, xcor_log, tag_align]
