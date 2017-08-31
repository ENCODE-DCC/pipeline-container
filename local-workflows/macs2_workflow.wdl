##TASK DEFINITIONS
task macs2 {
    File experiment
    File control
    File xcor_scores_input
    File chrom_sizes
    File narrowpeak_as
    File gappedpeak_as
    File broadpeak_as
    String genomesize
    String? prefix
    Int? fragment_length

    command {
        python /image_software/pipeline-container/src/macs2.py ${experiment} ${control} ${xcor_scores_input} ${chrom_sizes} ${narrowpeak_as} ${gappedpeak_as} ${broadpeak_as} ${genomesize} ${prefix} ${fragment_length}
    }

    output {
        File narrowpeaks_gzip = glob('*.narrowPeak.gz')[0]
        File gappedpeaks_gzip = glob('*.gappedPeak.gz')[0]
        File broadpeaks_gzip = glob('*.broadPeak.gz')[0]
        File narrowpeaks_bb = glob('*narrowPeak.bb')[0]
        File gappedpeaks_bb = glob('*gappedPeak.bb')[0]
        File broadpeaks_bb = glob('broadPeak.bb')[0]
        File fc_signal = glob('*.fc_signal.bw')[0]
        File pvalue_signal = glob('*.pvalue_signal.bw')
    }

    runtime {
        docker: 'quay.io/ottojolanki/macs2:test1'
        cpu: '1'
        memory: '4.0GB'
        disks: 'local-disk 30 HDD'
    }
}

