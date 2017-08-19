#TASK DEFINITIONS
#Looks like the if is usable only in the workflow, and not withing the tasks (at least until i'm able to prove otherwise)
#Circumvent this by defining two versions of the same task, with different length inputs.
task pool_and_pseudoreplicate_complex {
    Array[File] tags_rep1
    String paired_end

    command {
        python /image_software/pipeline-container/src/pool_and_pseudoreplicate.py ${tags_rep1[0]} ${tags_rep1[1]} ${paired_end} ${tags_rep1[2]} ${tags_rep1[3]} ${paired_end}
    }

    output {
        Array[File] out_files = glob('*.gz')
        File results = glob('pool_and_pseudoreplicate_outfiles.mapping')[0]
    }

    runtime {
        docker: 'quay.io/ottojolanki/pool_and_pseudoreplicate:v0.2'
        cpu: '1'
        memory: '4.0 GB'
        disks: 'local-disk 30 HDD'
    }
}

task pool_and_pseudoreplicate_simple {
    Array[File] tags_rep1
    String paired_end

    command {
        python /image_software/pipeline-container/src/pool_and_pseudoreplicate.py ${tags_rep1[0]} ${tags_rep1[1]} ${paired_end}
    }

    output {
        Array[File] out_files = glob('*.gz')
        File results = glob('pool_and_pseudoreplicate_outfiles.mapping')[0]
    }

    runtime {
        docker: 'quay.io/ottojolanki/pool_and_pseudoreplicate:v0.2'
        cpu: '1'
        memory: '4.0 GB'
        disks: 'local-disk 30 HDD'
    }
}


#WORKFLOW DEFINITION

workflow pool_and_pseudoreplicate_workflow {
    Array[File] tags_rep1
    String paired_end
    String genomesize
    File chrom_sizes
    File narrowpeak_as
    File gappedpeak_as
    File broadpeak_as

    if(length(tags_rep1)==4){
        call pool_and_pseudoreplicate_complex {
            input: tags_rep1=tags_rep1,
                   paired_end=paired_end
        }
    }
    if(length(tags_rep1)==2){
        call pool_and_pseudoreplicate_simple {
            input: tags_rep1=tags_rep1,
                   paired_end=paired_end
        }
    }

}
