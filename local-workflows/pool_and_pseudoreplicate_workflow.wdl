#TASK DEFINITIONS

task pool_and_pseudoreplicate {
    Array[File] tags_rep1
    String paired_end

    command {

        python /image_software/pipeline-container/src/pool_and_pseudoreplicate.py \
            ${sep=' ' tags_rep1} \
            ${paired_end}
    }

    output {

        Array[File] out_files=glob("*.gz")
        File results=glob("pool_and_pseudoreplicate_outfiles.json")[0]
    }

    runtime {
        docker: 'quay.io/ottojolanki/pool_and_pseudoreplicate:test2'
        cpu: '1'
        memory: '4.0 GB'
        disks: 'local-disk 30 HDD'
    }
}

#WORKFLOW DEFINITION

workflow pool_and_pseudoreplicate_workflow {
    Array[File] tags_rep1
    String paired_end

    call pool_and_pseudoreplicate {
        input: tags_rep1=tags_rep1,
               paired_end=paired_end
    }
}
