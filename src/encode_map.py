#!/usr/bin/env python2
# ENCODE_map 0.0.1

import os
import subprocess
import shlex
from multiprocessing import cpu_count
import logging
import sys


logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

BWA_PATH = "/image_software/bwa_0_7_10/bwa/bwa"
TRIMMOMATIC_PATH = "/image_software/Trimmomatic-0.36/trimmomatic-0.36.jar"

# the order of this list is important.
# strip_extensions strips from the right inward, so
# the expected right-most extensions should appear first (like .gz)
STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '.fa', '.fasta']


def strip_extensions(filename, extensions):
    basename = filename.split('/')[-1]
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
        reads1_filename = reads1_file
        reads1_basename = strip_extensions(reads1_filename, STRIP_EXTENSIONS)
        if reads2_file:
            end_string = "PE"
            reads2_filename = reads2_file
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
            SE_output = SE_output_filename
            cropped_reads = [SE_output]
        else:
            output_fwd_paired = output_fwd_paired_filename
            output_rev_paired = output_rev_paired_filename
            cropped_reads = [
                output_fwd_paired,
                output_rev_paired]

        output = dict(zip(["cropped_reads1", "cropped_reads2"], cropped_reads))

    logger.info("returning from crop with output %s" % (output))
    return output


def process(reads_file, reference_tar, bwa_aln_params, debug):
    # reads_file, reference_tar should be links to file objects.
    # reference_tar should be a tar of files generated by bwa index and
    # the tar should be uncompressed to avoid repeating the decompression.

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    bwa = BWA_PATH
    logger.info("In process with bwa %s" % (bwa))

    # Generate filename strings and download the files to the local filesystem
    reads_filename = reads_file
    reads_basename = strip_extensions(reads_filename, STRIP_EXTENSIONS)

    reference_tar_filename = reference_tar

    reference_dirname = '.'

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
    sai_dxfile = sai_filename
    output = {"suffix_array_index": sai_dxfile}
    logger.info("Returning from process with %s" % (output))
    return output

# always only read1, because each end is mapped independently
# probbaly should update code accordingly
def main( crop_length, reference_tar,
         bwa_aln_params, samtools_version, debug, reads1, reads2):
    # Main entry-point.  Parameter defaults assumed to come from dxapp.json.
    # reads1, reference_tar, reads2 are links to DNAnexus files or None

    # create a file handler
    handler = logging.FileHandler('mapping.log')

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

        crop_subjob = crop(reads1, reads2, crop_length, debug)

        unmapped_reads = [crop_subjob.get("cropped_reads1")]
        if paired_end:
            unmapped_reads.append(crop_subjob.get("cropped_reads2"))
        else:
            unmapped_reads.append(None)

    unmapped_reads = [r for r in unmapped_reads if r]

    for reads in unmapped_reads:
        mapping_subjob_input = {
            "reads_file": reads,
            "reference_tar": reference_tar,
            "bwa_aln_params": bwa_aln_params,
            "debug": debug
        }
        logger.info("Mapping job input: %s" % (mapping_subjob_input))

        process(reads, reference_tar, bwa_aln_params, debug)

    output = {
        "crop_length": crop_length,
        "paired_end": paired_end,
    }

    logger.info("Exiting mapping with output: %s" % (output))
    return output

if len(sys.argv) == 4:
    main(sys.argv[2], sys.argv[1], "-q 5 -l 32 -k 2", "1.0", False, sys.argv[3], None)
else:
    main(sys.argv[2], sys.argv[1], "-q 5 -l 32 -k 2", "1.0", False, sys.argv[3], sys.argv[4])
