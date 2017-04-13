#!/usr/bin/env python2
# ENCODE_map 0.0.1

import os
import subprocess
import shlex
import re
from multiprocessing import cpu_count
import dxpy
import common
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

BWA_PATH = {
    "0.7.7": "/tmp/bwa_0_7_7/bwa",
    "0.7.10": "/tmp/bwa_0_7_10/bwa"
}

SAMTOOLS_PATH = {
    "0.1.19": "/tmp/samtools_0_1_19/samtools/samtools",
    "1.0": "/tmp/samtools_1_0/samtools/samtools"
}

TRIMMOMATIC_PATH = "/tmp/Trimmomatic-0.36/trimmomatic-0.36.jar"

# the order of this list is important.
# strip_extensions strips from the right inward, so
# the expected right-most extensions should appear first (like .gz)
STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '.fa', '.fasta']


def strip_extensions(filename, extensions):
    basename = filename
    for extension in extensions:
        basename = basename.rpartition(extension)[0] or basename
    return basename


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


def resolve_reference(reference_tar_filename, reference_dirname):
    if reference_tar_filename.endswith('.gz') or reference_tar_filename.endswith('.tgz'):
        tar_command = \
            'tar -xzv --no-same-owner --no-same-permissions -C %s -f %s' \
            % (reference_dirname, reference_tar_filename)
    else:
        tar_command = \
            'tar -xv --no-same-owner --no-same-permissions -C %s -f %s' \
            % (reference_dirname, reference_tar_filename)
    print(subprocess.check_output(shlex.split('mkdir %s' % (reference_dirname))))
    logger.info("Unpacking %s with %s" % (reference_tar_filename, tar_command))
    print(subprocess.check_output(shlex.split(tar_command)))
    # assume the reference file is the only .fa or .fna file
    filename = next((f for f in os.listdir(reference_dirname) if f.endswith('.fa') or f.endswith('.fna') or f.endswith('.fa.gz') or f.endswith('.fna.gz')), None)
    return '/'.join([reference_dirname, filename])


def crop(reads1_file, reads2_file, crop_length, debug):

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.setLevel(logging.INFO)
    if crop_length == 'native':
        output = dict(zip(
            ["cropped_reads1", "cropped_reads2"], [reads1_file, reads2_file]))
    else:
        reads1_filename = reads1_file.name
        reads1_basename = strip_extensions(reads1_filename, STRIP_EXTENSIONS)
        if reads2_file:
            end_string = "PE"
            reads2_filename = reads2_file.name
            reads2_basename = \
                strip_extensions(reads2_filename, STRIP_EXTENSIONS)
            output_fwd_paired_filename = reads1_basename + '-crop-paired.fq.gz'
            output_fwd_unpaired_filename = \
                reads1_basename + '-crop-unpaired.fq.gz'
            output_rev_paired_filename = reads2_basename + '-crop-paired.fq.gz'
            output_rev_unpaired_filename = \
                reads2_basename + '-crop-unpaired.fq.gz'
            SE_output_filename = None
        else:
            end_string = "SE"
            reads2_filename = None
            reads2_basename = None
            output_fwd_paired_filename = None
            output_fwd_unpaired_filename = None
            output_rev_paired_filename = None
            output_rev_unpaired_filename = None
            SE_output_filename = reads1_basename + "-crop.fq.gz"

        crop_command = ' '.join([s for s in [
            'java -jar',
            TRIMMOMATIC_PATH,
            end_string,
            '-threads %d' % (cpu_count()),
            reads1_filename,
            reads2_filename,
            SE_output_filename,
            output_fwd_paired_filename,
            output_fwd_unpaired_filename,
            output_rev_paired_filename,
            output_rev_unpaired_filename,
            'MINLEN:%s' % (crop_length),
            'CROP:%s' % (crop_length)]
            if s])

        logger.info("Cropping with: %s" % (crop_command))
        print(subprocess.check_output(shlex.split(crop_command)))
        print(subprocess.check_output(shlex.split('ls -l')))

        if SE_output_filename:
            SE_output = dxpy.upload_local_file(SE_output_filename)
            cropped_reads = [dxpy.dxlink(SE_output), None]
        else:
            output_fwd_paired = output_fwd_paired_filename
            output_rev_paired = output_rev_paired_filename
            cropped_reads = [
                output_fwd_paired,
                output_rev_paired]

        output = dict(zip(["cropped_reads1", "cropped_reads2"], cropped_reads))

    logger.info("returning from crop with output %s" % (output))
    return output


def process(reads_file, reference_tar, bwa_aln_params, bwa_version, debug):
    # reads_file, reference_tar should be links to file objects.
    # reference_tar should be a tar of files generated by bwa index and
    # the tar should be uncompressed to avoid repeating the decompression.

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    bwa = BWA_PATH.get(bwa_version)
    assert bwa, "BWA version %s is not supported" % (bwa_version)
    logger.info("In process with bwa %s" % (bwa))

    # Generate filename strings and download the files to the local filesystem
    reads_filename = dxpy.describe(reads_file)['name']
    reads_file = dxpy.download_dxfile(reads_file, reads_filename)
    reads_basename = strip_extensions(reads_filename, STRIP_EXTENSIONS)

    reference_tar_filename = dxpy.describe(reference_tar)['name']
    dxpy.download_dxfile(reference_tar, reference_tar_filename)
    reference_dirname = 'reference_files'
    reference_filename = \
        resolve_reference(reference_tar_filename, reference_dirname)
    logger.info("Using reference file: %s" % (reference_filename))

    print(subprocess.check_output('ls -l', shell=True))

    # generate the suffix array index file
    sai_filename = '%s.sai' % (reads_basename)
    with open(sai_filename, 'w') as sai_file:
        # Build the bwa command and call bwa
        bwa_command = "%s aln %s -t %d %s %s" \
            % (bwa, bwa_aln_params, cpu_count(),
               reference_filename, reads_filename)
        logger.info("Running bwa with %s" % (bwa_command))
        subprocess.check_call(shlex.split(bwa_command), stdout=sai_file)

    print(subprocess.check_output('ls -l', shell=True))

    # Upload the output to the DNAnexus project
    logger.info("Uploading suffix array %s" % (sai_filename))
    sai_dxfile = dxpy.upload_local_file(sai_filename)
    output = {"suffix_array_index": dxpy.dxlink(sai_dxfile)}
    logger.info("Returning from process with %s" % (output))
    return output


@dxpy.entry_point("main")
def main(reads1, crop_length, reference_tar,
         bwa_version, bwa_aln_params, samtools_version, debug, reads2=None):

    # Main entry-point.  Parameter defaults assumed to come from dxapp.json.
    # reads1, reference_tar, reads2 are links to DNAnexus files or None

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

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

        crop_subjob = crop(reads1, reads2, crop_length, debug)

        unmapped_reads = [crop_subjob.get("cropped_reads1")]
        if paired_end:
            unmapped_reads.append(crop_subjob.get("cropped_reads2"))
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

#### Keep from here!!!!

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


