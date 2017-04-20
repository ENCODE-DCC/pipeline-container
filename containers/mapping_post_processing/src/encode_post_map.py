#!/usr/bin/env python2
# ENCODE_map 0.0.1

import os
import subprocess
import shlex
import re
from multiprocessing import cpu_count
import common
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

SAMTOOLS_PATH = {
    "0.1.19": "/tmp/samtools_0_1_19/samtools/samtools",
    "1.0": "/tmp/samtools_1_0/samtools/samtools"
}

BWA_PATH = {

    "0.7.10": "/tmp/bwa_0_7_10/bwa/bwa"
}
# the order of this list is important.
# strip_extensions strips from the right inward, so
# the expected right-most extensions should appear first (like .gz)
STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '.fa', '.fasta']


def strip_extensions(filename, extensions):
    basename = filename
    for extension in extensions:
        basename = basename.rpartition(extension)[0] or basename
    return basename


def resolve_reference(reference_tar_filename, reference_dirname):
    if reference_tar_filename.endswith('.gz') or reference_tar_filename.endswith('.tgz'):
        tar_command = \
            'tar -xzv --no-same-owner --no-same-permissions -C %s -f %s' \
            % (reference_dirname, reference_tar_filename)
    else:
        tar_command = \
            'tar -xv --no-same-owner --no-same-permissions -C %s -f %s' \
            % (reference_dirname, reference_tar_filename)

    logger.info("Unpacking %s with %s" % (reference_tar_filename, tar_command))

    print(subprocess.check_output(shlex.split(tar_command)))

    # assume the reference file is the only .fa or .fna file
    filename = next((f for f in os.listdir(reference_dirname) if f.endswith('.fa') or f.endswith('.fna') or f.endswith('.fa.gz') or f.endswith('.fna.gz')), None)
    return '/'.join([reference_dirname, filename])


def flagstat_parse(fname):
    with open(fname, 'r') as flagstat_file:
        if not flagstat_file:
            return None
        flagstat_lines = flagstat_file.read().splitlines()

    qc_dict = {
        # values are regular expressions,
        # will be replaced with scores [hiq, lowq]
        'in_total': 'in total',
        'duplicates': 'duplicates',
        'mapped': 'mapped',
        'paired_in_sequencing': 'paired in sequencing',
        'read1': 'read1',
        'read2': 'read2',
        'properly_paired': 'properly paired',
        'with_self_mate_mapped': 'with itself and mate mapped',
        'singletons': 'singletons',
        # i.e. at the end of the line
        'mate_mapped_different_chr': 'with mate mapped to a different chr$',
        # RE so must escape
        'mate_mapped_different_chr_hiQ':
            'with mate mapped to a different chr \(mapQ>=5\)'
    }

    for (qc_key, qc_pattern) in qc_dict.items():
        qc_metrics = next(re.split(qc_pattern, line)
                          for line in flagstat_lines
                          if re.search(qc_pattern, line))
        (hiq, lowq) = qc_metrics[0].split(' + ')
        qc_dict[qc_key] = [int(hiq.rstrip()), int(lowq.rstrip())]

    return qc_dict


def postprocess(indexed_reads, unmapped_reads, crop_length, reference_tar,
                bwa_version, samtools_version, debug):

    handler = logging.FileHandler('post_mapping.log')

    if debug:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    samtools = SAMTOOLS_PATH.get(samtools_version)
    assert samtools, "samtools version %s is not supported" % (samtools_version)
    bwa = BWA_PATH.get(bwa_version)
    assert bwa, "BWA version %s is not supported" % (bwa_version)
    logger.info("In postprocess with samtools %s and bwa %s" % (samtools, bwa))

    indexed_reads_filenames = []
    unmapped_reads_filenames = []
    #print (indexed_reads)

    for i, reads in enumerate(indexed_reads):
        #print (str(i) + '\t' + str(reads))
        read_pair_number = i+1
        logger.info("indexed_reads %d: %s" % (read_pair_number, reads))
        indexed_reads_filenames.append(reads)

        unmapped = unmapped_reads[i]
        logger.info("unmapped reads %d: %s" % (read_pair_number, unmapped))
        unmapped_reads_filenames.append(unmapped)

    reference_tar_filename = reference_tar
    logger.info("reference_tar: %s" % (reference_tar_filename))
    # extract the reference files from the tar
    reference_dirname = '/tmp/reference_files'

    reference_filename = \
        resolve_reference(reference_tar_filename, reference_dirname)


    logger.info("Using reference file: %s" % (reference_filename))

    paired_end = len(indexed_reads) == 2

    if paired_end:
        r1_basename = strip_extensions(
            unmapped_reads_filenames[0], STRIP_EXTENSIONS)
        r2_basename = strip_extensions(
            unmapped_reads_filenames[1], STRIP_EXTENSIONS)
        reads_basename = r1_basename + r2_basename
    else:
        reads_basename = strip_extensions(
            unmapped_reads_filenames[0], STRIP_EXTENSIONS)
    raw_bam_filename = '%s.raw.srt.bam' % (reads_basename)
    raw_bam_mapstats_filename = '%s.raw.srt.bam.flagstat.qc' % (reads_basename)

    if paired_end:
        reads1_filename = indexed_reads_filenames[0]
        reads2_filename = indexed_reads_filenames[1]
        unmapped_reads1_filename = unmapped_reads_filenames[0]
        unmapped_reads2_filename = unmapped_reads_filenames[1]
        raw_sam_filename = reads_basename + ".raw.sam"
        badcigar_filename = "badreads.tmp"
        steps = [
            "%s sampe -P %s %s %s %s %s"
            % (bwa, reference_filename, reads1_filename, reads2_filename,
               unmapped_reads1_filename, unmapped_reads2_filename),
            "tee %s" % (raw_sam_filename),
            r"""awk 'BEGIN {FS="\t" ; OFS="\t"} ! /^@/ && $6!="*" { cigar=$6; gsub("[0-9]+D","",cigar); n = split(cigar,vals,"[A-Z]"); s = 0; for (i=1;i<=n;i++) s=s+vals[i]; seqlen=length($10) ; if (s!=seqlen) print $1"\t" ; }'""",
            "sort",
            "uniq"]
        out, err = common.run_pipe(steps, badcigar_filename)
        print(out)
        if err:
            logger.error("sampe error: %s" % (err))

        steps = [
            "cat %s" % (raw_sam_filename),
            "grep -v -F -f %s" % (badcigar_filename)]
    else:  # single end
        reads_filename = indexed_reads_filenames[0]
        unmapped_reads_filename = unmapped_reads_filenames[0]
        steps = [
            "%s samse %s %s %s"
            % (bwa, reference_filename,
               reads_filename, unmapped_reads_filename)]

    if samtools_version == "0.1.9":
        steps.extend([
            "%s view -Su -" % (samtools),
            "%s sort - %s"
            % (samtools, raw_bam_filename.rstrip('.bam'))])  # samtools adds .bam
    else:
        steps.extend([
            "%s view -@%d -Su -" % (samtools, cpu_count()),
            "%s sort -@%d - %s"
            % (samtools, cpu_count(), raw_bam_filename.rstrip('.bam'))])  # samtools adds .bam

    logger.info("Running pipe: %s" % (steps))
    out, err = common.run_pipe(steps)

    if out:
        print(out)
    if err:
        logger.error("samtools error: %s" % (err))

    with open(raw_bam_mapstats_filename, 'w') as fh:
        subprocess.check_call(
            shlex.split("%s flagstat %s" % (samtools, raw_bam_filename)),
            stdout=fh)
    print(subprocess.check_output('ls -l', shell=True))

    mapped_reads = raw_bam_filename
    mapping_statistics = raw_bam_mapstats_filename
    flagstat_qc = flagstat_parse(raw_bam_mapstats_filename)

    output = {
        'mapped_reads': mapped_reads,
        'mapping_statistics': mapping_statistics,
        'n_mapped_reads': flagstat_qc.get('mapped')[0],  # 0 is hi-q reads
        "crop_length": crop_length,
        "paired_end": paired_end
    }
    logger.info("Returning from postprocess with output: %s" % (output))
    return output


'''def main(reads1, crop_length, reference_tar,
         bwa_version, bwa_aln_params, samtools_version, debug, reads2=None):

    # Main entry-point.  Parameter defaults assumed to come from dxapp.json.
    # reads1, reference_tar, reads2 are links to DNAnexus files or None

    # create a file handler
    handler = logging.FileHandler('post_mapping.log')

    if debug:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    # This spawns only one or two subjobs for single- or paired-end,
    # respectively.  It could also download the files, chunk the reads,
    # and spawn multiple subjobs.

    # Files are downloaded later by subjobs into their own filesystems
    # and uploaded to the project.

    # Initialize file handlers for input files.

    paired_end = reads2 is not None

    if crop_length == 'native':
        crop_subjob = None
        unmapped_reads = [reads1, reads2]
    else:
        crop_subjob_input = {
            "reads1_file": reads1,
            "reads2_file": reads2,
            "crop_length": crop_length,
            "debug": debug
        }
        logger.info("Crop job input: %s" % (crop_subjob_input))
        crop_subjob = dxpy.new_dxjob(crop_subjob_input, "crop")
        unmapped_reads = [crop_subjob.get_output_ref("cropped_reads1")]
        if paired_end:
            unmapped_reads.append(crop_subjob.get_output_ref("cropped_reads2"))
        else:
            unmapped_reads.append(None)

    unmapped_reads = [r for r in unmapped_reads if r]

    mapping_subjobs = []
    for reads in unmapped_reads:
        mapping_subjob_input = {
            "reads_file": reads,
            "reference_tar": reference_tar,
            "bwa_aln_params": bwa_aln_params,
            "bwa_version": bwa_version,
            "debug": debug
        }
        logger.info("Mapping job input: %s" % (mapping_subjob_input))
        if crop_subjob:
            mapping_subjobs.append(dxpy.new_dxjob(
                fn_input=mapping_subjob_input,
                fn_name="process",
                depends_on=[crop_subjob]))
        else:
            mapping_subjobs.append(dxpy.new_dxjob(
                fn_input=mapping_subjob_input,
                fn_name="process"))

    # Create the job that will perform the "postprocess" step.
    # depends_on=mapping_subjobs, so blocks on all mapping subjobs

    postprocess_job = dxpy.new_dxjob(
        fn_input={
            "indexed_reads": [
                subjob.get_output_ref("suffix_array_index")
                for subjob in mapping_subjobs],
            "unmapped_reads": unmapped_reads,
            "reference_tar": reference_tar,
            "bwa_version": bwa_version,
            "samtools_version": samtools_version,
            "debug": debug},
        fn_name="postprocess",
        depends_on=mapping_subjobs)

    mapped_reads = postprocess_job.get_output_ref("mapped_reads")
    mapping_statistics = postprocess_job.get_output_ref("mapping_statistics")
    n_mapped_reads = postprocess_job.get_output_ref("n_mapped_reads")

    output = {
        "mapped_reads": mapped_reads,
        "crop_length": crop_length,
        "mapping_statistics": mapping_statistics,
        "paired_end": paired_end,
        "n_mapped_reads": n_mapped_reads
    }
    logger.info("Exiting with output: %s" % (output))
    return output

main('/tmp/container/portion.bam', False, '', False)
main('/tmp/container/part.ENCFF000RQF.fastq.gz', '20',
'/tmp/container/ENCFF643CGH.tar.gz', "-q 5 -l 32 -k 2", "1.0", False)

'''
postprocess(['/tmp/container/part.ENCFF000RQF-crop.sai'],
            ['/tmp/container/part.ENCFF000RQF-crop.fq.gz'],
            '20', '/tmp/container/ENCFF643CGH.tar.gz',
            '0.7.10', '0.1.19', False)
