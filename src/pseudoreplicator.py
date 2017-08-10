#!/usr/bin/env python
# pseudoreplicator 0.0.1

import subprocess
import re
import gzip
import common
import logging
import sys
import os


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def main(input_tags, prefix=None):
    input_tags_filename = input_tags

    # introspect the file to determine tagAlign (thus SE) or BEDPE (thus PE)
    # strip extension as appropriate

    subprocess.check_output('ls', shell=True)
    with gzip.open(input_tags_filename) as f:
        firstline = f.readline()
    logger.info('First line of input_tags:\n%s' % (firstline))

    se_cols = 6
    pe_cols = 10
    if re.match('^(\S+[\t\n]){%d}$' % (se_cols), firstline):
        paired_end = False
        input_tags_basename = prefix or input_tags_filename.rstrip('.tagAlign.gz')
        filename_infix = 'SE'
        logger.info("Detected single-end data")
    elif re.match('^(\S+[\t\n]){%d}$' % (pe_cols), firstline):
        paired_end = True
        input_tags_basename = prefix or input_tags_filename.rstrip('.bedpe.gz')
        filename_infix = 'PE2SE'
        logger.info("Detected paired-end data")
    else:
        raise IOError(
            "%s is neither a BEDPE or tagAlign file" % (input_tags_filename))
    #fixed filename -> basename in pr2
    pr_ta_filenames = \
        [input_tags_basename + ".%s.pr1.tagAlign.gz" % (filename_infix),
         input_tags_basename + ".%s.pr2.tagAlign.gz" % (filename_infix)]

    # count lines in the file
    out, err = common.run_pipe([
        'gzip -dc %s' % (input_tags_filename),
        'wc -l'])
    # number of lines in each split
    nlines = (int(out)+1)/2
    # Shuffle and split BEDPE file into 2 equal parts
    # by using the input to seed shuf we ensure multiple runs with the same
    # input will produce the same output
    # Produces two files named splits_prefix0n, n=1,2
    splits_prefix = 'temp_split'
    # omitted the -d from split and changed index to 'aa', 'ab' this works on both mac and ubuntu, shuf only on ubuntu
    out, err = common.run_pipe([
        'gzip -dc %s' % (input_tags_filename),
        'shuf --random-source=%s' % (input_tags_filename),
        'split -a 2 -l %d - %s' % (nlines, splits_prefix)])
    # Convert read pairs to reads into standard tagAlign file
    for i, index in enumerate(['aa', 'ab']):  # could be made multi-threaded
        steps = ['cat %s' % (splits_prefix+index)]
        if paired_end:
            steps.extend([r"""awk 'BEGIN{OFS="\t"}{printf "%s\t%s\t%s\tN\t1000\t%s\n%s\t%s\t%s\tN\t1000\t%s\n",$1,$2,$3,$9,$4,$5,$6,$10}'"""])
        steps.extend(['gzip -cn'])
        out, err = common.run_pipe(steps, outfile=pr_ta_filenames[i])
        os.remove(splits_prefix + index)

    pseudoreplicate1_file = pr_ta_filenames[0]
    pseudoreplicate2_file = pr_ta_filenames[1]

    output = {
        "pseudoreplicate1": pseudoreplicate1_file,
        "pseudoreplicate2": pseudoreplicate2_file
    }

    print output
    return output


if __name__ == "__main__":
    main(sys.argv[1])
