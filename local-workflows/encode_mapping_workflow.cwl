cwlVersion: v1.0

class: Workflow

inputs:

  - id: trimming_parameter
    type: string

  - id: fastqs
    type: File[]

  - id: reference
    type: File

outputs: 

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
  output_dir:
    type: Directory
    outputSource: output_folder/folder

steps:
  mapper:
    run: mapping.cwl
    in:
      reference_file: reference
      trimming_length: trimming_parameter
      fastq_files: fastqs
    out: [unmapped_files, sai_files, mapping_log]

  post_processing:
    run: post_processing.cwl
    in:
     
      trimming_length: trimming_parameter
      reference_file: reference
      unmapped_fastqs: mapper/unmapped_files
      sai_files: mapper/sai_files
    out: [unfiltered_bam, unfiltered_flagstats, post_mapping_log]

  filter_qc:
    run: filter_qc.cwl
    in:
      bam_file: post_processing/unfiltered_bam
    out: [filtered_bam, filtered_bam_bai, filtered_map_stats, dup_file_qc, pbc_file_qc, filter_qc_log]

  xcor:
    run: xcor.cwl
    in:
      bam_file: filter_qc/filtered_bam
      fastq_files: fastqs
    out: [cc_file, cc_plot, xcor_log, tag_align]

  output_folder:
    run: mount_folder.cwl
    in: 
      unfiltered_bam: post_processing/unfiltered_bam
      filtered_bam: filter_qc/filtered_bam
      unfiltered_flagstat: post_processing/unfiltered_flagstats
      filtered_flagstat: filter_qc/filtered_map_stats
      dup_qc: filter_qc/dup_file_qc
      pbc_qc: filter_qc/pbc_file_qc
      mapping_log: mapper/mapping_log
      post_mapping_log: post_processing/post_mapping_log
      filter_qc_log: filter_qc/filter_qc_log
      xcor_log: xcor/xcor_log
      cc: xcor/cc_file
      cc_pdf: xcor/cc_plot
      tag_align: xcor/tag_align
    out: [folder]