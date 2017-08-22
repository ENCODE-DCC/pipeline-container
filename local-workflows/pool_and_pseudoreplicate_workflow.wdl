#TASK DEFINITIONS
#Looks like the if is usable only in the workflow, and not withing the tasks (at least until i'm able to prove otherwise)
#Circumvent this by defining two versions of the same task, with different length inputs.
#Name all the outputs, and inputs avoid Arrays to be able to pair correct files in the cross-correlation step
task pool_and_pseudoreplicate_complex {
    File tags_rep1
    File tags_rep2
    File tags_ctrl1
    File tags_ctrl2
    String rep1_paired_end
    String rep2_paired_end

    command {
        python /image_software/pipeline-container/src/pool_and_pseudoreplicate.py ${tags_rep1} ${tags_ctrl1} ${rep1_paired_end} ${tags_rep2} ${tags_ctrl2} ${rep2_paired_end}
    }

    output {
        Array[File] out_files = glob('*.gz')
        File results = glob('pool_and_pseudoreplicate_outfiles.mapping')[0]
    }

    runtime {
        docker: 'quay.io/ottojolanki/pool_and_pseudoreplicate:v1.11'
        cpu: '1'
        memory: '4.0 GB'
        disks: 'local-disk 30 HDD'
    }
}

task pool_and_pseudoreplicate_simple {
    File tags_rep1
    File tags_ctrl1
    String rep1_paired_end

    command {
        python /image_software/pipeline-container/src/pool_and_pseudoreplicate.py ${tags_rep1} ${tags_ctrl1} ${rep1_paired_end}
    }

    output {
        File rep1_pr1 = glob('*pr1.tagAlign.gz')[0]
        File rep1_pr2 = glob('*pr2.tagAlign.gz')[0]
        File results = glob('pool_and_pseudoreplicate_outfiles.mapping')[0]
    }

    runtime {
        docker: 'quay.io/ottojolanki/pool_and_pseudoreplicate:v1.11'
        cpu: '1'
        memory: '4.0 GB'
        disks: 'local-disk 30 HDD'
    }
}

task xcor {
    File tags
    String paired_end

    command {
        python /image_software/pipeline-container/src/xcor_only.py ${tags} ${paired_end}
    }

    output {
        File xcor_scores = glob('*.cc.qc')[0]
        File xcor_plot = glob('*.cc.plot.pdf')[0]

    }

    runtime {
        docker: 'quay.io/ottojolanki/xcor_only:v0.2'
        cpu: '1'
        memory: '4.0GB'
        disks: 'local-disk 30 HDD'
    }
}

#WORKFLOW DEFINITION

workflow pool_and_pseudoreplicate_workflow {
    File tags_rep1
    File? tags_rep2
    File tags_ctrl1
    File? tags_ctrl2
    String rep1_paired_end
    String? rep2_paired_end
    #String genomesize
    #File chrom_sizes
    #File narrowpeak_as
    #File gappedpeak_as
    #File broadpeak_as

    if(defined(tags_rep2)){
        call pool_and_pseudoreplicate_complex {
            input:  tags_rep1=tags_rep1,
                    tags_rep2=tags_rep2,
                    tags_ctrl1=tags_ctrl1,
                    tags_ctrl2=tags_ctrl2,
                    rep1_paired_end=rep1_paired_end,
                    rep2_paired_end=rep2_paired_end
        }
    }
    if(!defined(tags_rep2)){
        call pool_and_pseudoreplicate_simple {
            input:  tags_rep1=tags_rep1,
                    tags_ctrl1=tags_ctrl1,
                    rep1_paired_end=rep1_paired_end
        }

        call xcor {
            input:  tags = pool_and_pseudoreplicate_simple.rep1_pr1,
                    paired_end = rep1_paired_end
        }
    }

}
