#!/usr/bin/env python2
# ENCODE_map 0.0.1

import os
import subprocess
import shlex
import re
from multiprocessing import cpu_count
import common
import logging
import sys

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

SAMTOOLS_PATH = {
    "0.1.19": "/image_software/samtools_0_1_19/samtools/samtools",
    "1.0": "/image_software/samtools_1_0/samtools/samtools"
}

BWA_PATH = {

    "0.7.10": "/image_software/bwa_0_7_10/bwa/bwa"
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

def special_sort(reads_files):
    to_sort = []
    for f in reads_files:
        to_sort.append(f.split('/')[-1])
    sorted_names = sorted(to_sort)

    sorting_result = []
    for n in sorted_names:
        for x in reads_files:
            if x.endswith(n) and x.find('crop-unpaired') == -1:
                sorting_result.append(x)
                break
    return sorting_result


def figure_out_sort(reads_files, unmapped_reads, indexed_reads):
    initial_order_flag = False
    initial_files = []
    unmapped_not_sorted = []
    sai_not_sorted = []
    for entry in reads_files:
        if entry.endswith('.sai'):
            initial_order_flag = True
            sai_not_sorted.append(entry)
        if (not entry.endswith('.sai')) and initial_order_flag:
            initial_files.append(entry)
        if (not entry.endswith('.sai')) and (not initial_order_flag):
            unmapped_not_sorted.append(entry)

    for entry in initial_files:
        prefix = '.'.join(entry.split('/')[-1].split('.')[:-2])
        for path in unmapped_not_sorted:
            if path.find(prefix) != -1:
                unmapped_reads.append(path)
                break
        for path in sai_not_sorted:
            if path.find(prefix) != -1 and path.find('crop-unpaired') == -1:
                indexed_reads.append(path)
                break
    return


def postprocess(crop_length, reference_tar,
                bwa_version, samtools_version, debug, reads_files):

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

    indexed_reads = []
    unmapped_reads = []

    '''for file_name in special_sort(reads_files):
        if file_name.endswith('.sai'):
            indexed_reads.append(file_name)
        else:
            unmapped_reads.append(file_name)
    '''
    figure_out_sort(reads_files, unmapped_reads, indexed_reads)
    print (indexed_reads)
    print (unmapped_reads)
    indexed_reads_filenames = []
    unmapped_reads_filenames = []

    for i, reads in enumerate(indexed_reads):
        read_pair_number = i+1
        logger.info("indexed_reads %d: %s" % (read_pair_number, reads))
        indexed_reads_filenames.append(reads)

        unmapped = unmapped_reads[i]
        logger.info("unmapped reads %d: %s" % (read_pair_number, unmapped))
        unmapped_reads_filenames.append(unmapped)

    print (indexed_reads_filenames)
    print (unmapped_reads_filenames)
    reference_tar_filename = reference_tar
    logger.info("reference_tar: %s" % (reference_tar_filename))
    # extract the reference files from the tar
    reference_dirname = '.'

    reference_filename = \
        resolve_reference(reference_tar_filename, reference_dirname)

    logger.info("Using reference file: %s" % (reference_filename))

    paired_end = len(indexed_reads) == 2

    # fixing the directories
    if paired_end:
        r1_basename = (strip_extensions(
            unmapped_reads_filenames[0], STRIP_EXTENSIONS)).split('/')[-1]
        r2_basename = (strip_extensions(
            unmapped_reads_filenames[1], STRIP_EXTENSIONS)).split('/')[-1]
        reads_basename = r1_basename + r2_basename
    else:
        reads_basename = (strip_extensions(
            unmapped_reads_filenames[0], STRIP_EXTENSIONS)).split('/')[-1]

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

postprocess(sys.argv[1],
            sys.argv[2],
            '0.7.10', '0.1.19', False, sys.argv[3:])
