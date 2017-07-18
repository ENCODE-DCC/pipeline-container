## This WDL maps FASTQ file(s) using ENCODE ChIP-seq mapping pipeline
##
## Requirements/expectations :
## - trimming length parameter (either "native" or lenght in string format)
## - fastq (either one SE or two PE fastq file(s))
## - reference (BWA tar reference index file)
##
## example inputs.json would look like:
## {
##      "encode_mapping_workflow.fastqs": ["/.../Documents/dockerFiles/rep1-ENCFF000VOL-chr21.fq.gz"],
##      "encode_mapping_workflow.trimming_parameter": "native",
##      "encode_mapping_workflow.reference": "/.../dockerFiles/GRCh38_chr21_bwa.tar.gz"
## }



# TASK DEFINITIONS

task filter_qc {
    File bam_file
    Array[File] fastq_files

    command {

        python /image_software/pipeline-container/src/filter_qc.py \
         ${bam_file} \
         ${sep=' ' fastq_files}
    }

    output {
        File dup_file_qc = glob('*.dup.qc')[0]
        File filter_qc_log = glob('*ilter_qc.log')[0]
        File filtered_bam = glob('*final.bam')[0]
        File filtered_bam_bai = glob('*final.bam.bai')[0]
        File filtered_map_stats = glob('*final.flagstat.qc')[0]
        File pbc_file_qc = glob('*.pbc.qc')[0]
    }

    runtime {
        docker: 'quay.io/gabdank/filter:0622.1'
        cpu: '1'
        memory: '4092 MB'
        disks: 'local-disk 512 HDD'
    }
}


task mapping {
    Array[File] fastq_files
    File reference_file
    String trimming_length

    command {

        python /image_software/pipeline-container/src/encode_map.py \
         ${reference_file} \
         ${trimming_length} \
         ${sep=' ' fastq_files}
    }

    output {
        File mapping_log = glob('mapping.log')[0]
        Array[File] sai_files = glob('*.sai')
        Array[File] unmapped_files = glob('*.gz')
    }

    runtime {
        docker: 'quay.io/gabdank/mapping:0622.1'
        cpu: '1'
        memory: '4092 MB'
        disks: 'local-disk 512 HDD'
    }
}


task xcor {
    File bam_file
    Array[File] fastq_files

    command {

        python /image_software/pipeline-container/src/xcor.py \
         ${bam_file} \
         ${sep=' ' fastq_files}
    }

    output {
        File cc_file = glob('*.cc.qc')[0]
        File cc_plot = glob('*.cc.plot.pdf')[0]
        Array[File] tag_align = glob('*tag*')
        File xcor_log = glob('xcor.log')[0]
    }

    runtime {
        docker: 'quay.io/gabdank/xcor:0622.1'
        cpu: '1'
        memory: '4092 MB'
        disks: 'local-disk 512 HDD'
    }
}


task post_processing {
    Array[File] initial_fastqs
    File reference_file
    Array[File] sai_files
    String trimming_length
    Array[File] unmapped_fastqs

    command {

        python /image_software/pipeline-container/src/encode_post_map.py \
         ${trimming_length} \
         ${reference_file} \
         ${sep=' ' unmapped_fastqs} \
         ${sep=' ' sai_files} \
         ${sep=' ' initial_fastqs}
    }

    output {
        File post_mapping_log = glob('post_mapping.log')[0]
        File unfiltered_bam = glob('*.raw.srt.bam')[0]
        File unfiltered_flagstats = glob('*.raw.srt.bam.flagstat.qc')[0]
    }

    runtime {
        docker: 'quay.io/gabdank/post_mapping:0622.1'
        cpu: '1'
        memory: '4092 MB'
        disks: 'local-disk 512 HDD'
    }
}

task gather_the_outputs {

    File unfiltered_bam
    File filtered_bam
    File unfiltered_flagstat
    File filtered_flagstat
    File dup_qc
    File pbc_qc
    File mapping_log
    File post_mapping_log
    File filter_qc_log
    File xcor_log
    File cc
    File cc_pdf
    Array[File] tag_align


    command {
        cp ${unfiltered_bam} .
        cp ${filtered_bam} .
        cp ${unfiltered_flagstat} .
        cp ${filtered_flagstat} .
        cp ${dup_qc} .
        cp ${pbc_qc} .
        cp ${mapping_log} .
        cp ${post_mapping_log} .
        cp ${filter_qc_log} .
        cp ${xcor_log} .
        cp ${cc} .
        cp ${cc_pdf} .
        cp ${sep=' ' tag_align} .
    }
}

# WORKFLOW DEFINITION

workflow encode_mapping_workflow {
    String trimming_parameter
    Array[File] fastqs
    File reference


    call mapping  {
        input: fastq_files=fastqs,
          reference_file=reference,
          trimming_length=trimming_parameter
    }

    call post_processing  {
        input: initial_fastqs=fastqs,
          reference_file=reference,
          sai_files=mapping.sai_files,
          trimming_length=trimming_parameter,
          unmapped_fastqs=mapping.unmapped_files
    }

    call filter_qc  {
        input: bam_file=post_processing.unfiltered_bam,
          fastq_files=fastqs
    }


    call xcor  {
        input: bam_file=filter_qc.filtered_bam,
          fastq_files=fastqs
    }

    call gather_the_outputs {
        input: cc = xcor.cc_file,
          cc_pdf = xcor.cc_plot,
          dup_qc = filter_qc.dup_file_qc,
          filter_qc_log = filter_qc.filter_qc_log,
          filtered_bam = filter_qc.filtered_bam,
          filtered_flagstat = filter_qc.filtered_map_stats,
          mapping_log = mapping.mapping_log,
          pbc_qc = filter_qc.pbc_file_qc,
          post_mapping_log = post_processing.post_mapping_log,
          tag_align = xcor.tag_align,
          unfiltered_bam = post_processing.unfiltered_bam,
          unfiltered_flagstat = post_processing.unfiltered_flagstats,
          xcor_log = xcor.xcor_log
    }

}


