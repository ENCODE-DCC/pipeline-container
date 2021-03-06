#!/usr/bin/env python
# pool_and_pseudoreplicate.py 0.0.1


import subprocess
import common
import logging
from os.path import splitext
import sys
import re
import os
import gzip
import json

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def parse_true_or_false(truth):
        return truth.lower() == 'true'


def pool(inputs, prefix=None):

    input_filenames = inputs

    # uses last extension - presumably they are all the same
    extension = splitext(splitext(input_filenames[-1])[0])[1]
    if prefix:
        pooled_filename = prefix + "_pooled%s.gz" % (extension)
    else:
        pooled_filename = \
            '-'.join([splitext(splitext(fn)[0])[0] for fn in input_filenames]) + "_pooled%s.gz" % (extension)
    # outfile needs to be reduced to basename to direct cromwell
    # output to the correct place
    out, err = common.run_pipe([
        'gzip -dc %s' % (' '.join(input_filenames)),
        'gzip -cn'],
        outfile=os.path.basename(pooled_filename))

    output = {
        "pooled": pooled_filename
    }

    return output


def pseudoreplicator(input_tags, prefix=None):
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
    # fixed filename -> basename in pr2
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
        # outfile needs to be reduced to basename to direct cromwell
        # output into correct place
        out, err = common.run_pipe(steps, outfile=os.path.basename(pr_ta_filenames[i]))
        os.remove(splits_prefix + index)

    pseudoreplicate1_file = pr_ta_filenames[0]
    pseudoreplicate2_file = pr_ta_filenames[1]

    output = {
        "pseudoreplicate1": pseudoreplicate1_file,
        "pseudoreplicate2": pseudoreplicate2_file
    }

    return output
# arguments not needed for the first image:
# chrom_sizes
# genomesize
# {narrow, broad, gapped}peaks
# fragment_length
# xcor (gets calculated separately before macs2)


def main(rep1_ta, ctl1_ta, rep1_paired_end,
         rep2_ta=None, ctl2_ta=None, rep2_paired_end=None):
    rep1_ta_filename = rep1_ta
    ntags_rep1 = common.count_lines(rep1_ta_filename)
    output = {'rep1_ta': rep1_ta_filename}

    simplicate_experiment = rep1_ta and not rep2_ta
    output.update({'simplicate_experiment': simplicate_experiment})
    if simplicate_experiment:
        logger.info("No rep2 tags specified so processing as a simplicate experiment.")
    else:
        logger.info("Rep1 and rep2 tags specified so processing as a replicated experiment.")
        output.update({'rep2_ta': rep2_ta})

    if not simplicate_experiment:
        assert rep1_paired_end == rep2_paired_end, 'Mixed PE/SE not supported'
        rep2_ta_filename = rep2_ta
        ntags_rep2 = common.count_lines(rep2_ta_filename)
        output.update({'rep2_ta': rep2_ta_filename})
    paired_end = rep1_paired_end
    output.update({'paired_end': paired_end})
    unary_control = (ctl1_ta == ctl2_ta) or not ctl2_ta
    ctl1_ta_filename = ctl1_ta

    if not unary_control:
        ctl2_ta_filename = ctl2_ta
    else:
        ctl2_ta_filename = ctl1_ta

    ntags_ctl1 = common.count_lines(ctl1_ta_filename)
    ntags_ctl2 = common.count_lines(ctl2_ta_filename)
    rep1_control = ctl1_ta  # default.  May be changed later.
    rep2_control = ctl2_ta  # default.  May be changed later.
    output.update({'rep1_control': rep1_control,
                   'rep2_control': rep2_control})

    rep_info = [(ntags_rep1, 'replicate 1', rep1_ta_filename)]
    if not simplicate_experiment:
        rep_info.append((ntags_rep2, 'replicate 2', rep2_ta_filename))
    rep_info.extend(
        [(ntags_ctl1, 'control 1', ctl1_ta_filename),
         (ntags_ctl2, 'control 2', ctl2_ta_filename)])
    for n, name, filename in rep_info:
        logger.info("Found %d tags in %s file %s" % (n, name, filename))

    subprocess.check_output('ls -l', shell=True, stderr=subprocess.STDOUT)

    if not simplicate_experiment:
        pool_replicates_subjob = \
            pool(**{"inputs": [rep1_ta, rep2_ta],
                 "prefix": 'pooled_reps'})
        pooled_replicates = pool_replicates_subjob.get("pooled")
        output.update({'pooled_replicates': pooled_replicates})
        # this needs to go to the other image
        '''
        pooled_replicates_xcor_subjob = \
            xcor_only(
                pooled_replicates,
                paired_end,
                name='Pool cross-correlation')
        '''

    if unary_control:
        logger.info("Only one control supplied.")
        if not simplicate_experiment:
            logger.info("Using one control for both replicate 1 and 2 and for the pool.")
        rep2_control = rep1_control
        control_for_pool = rep1_control
        output.update({'rep2_control': rep2_control,
                       'control_for_pool': rep1_control})
    else:
        pool_controls_subjob = pool(
            **{"inputs": [ctl1_ta, ctl2_ta],
               "prefix": "PL_ctls"})
        pooled_controls = pool_controls_subjob.get("pooled")
        # always use the pooled controls for the pool
        control_for_pool = pooled_controls
        output.update({'control_for_pool': control_for_pool})
        # use the pooled controls for the reps depending on the ratio of rep to
        # control reads
        ratio_ctl_reads = float(ntags_ctl1)/float(ntags_ctl2)
        if ratio_ctl_reads < 1:
                ratio_ctl_reads = 1/ratio_ctl_reads
        ratio_cutoff = 1.2
        if ratio_ctl_reads > ratio_cutoff:
                logger.info(
                    "Number of reads in controls differ by > factor of %f. Using pooled controls."
                    % (ratio_cutoff))
                rep1_control = pooled_controls
                rep2_control = pooled_controls
                output.update({'rep1_control': pooled_controls,
                               'rep2_control': pooled_controls})
        else:
                if ntags_ctl1 < ntags_rep1:
                        logger.info("Fewer reads in control replicate 1 than experiment replicate 1.  Using pooled controls for replicate 1.")
                        rep1_control = pooled_controls
                        output.update({'rep1_control': pooled_controls})
                elif not simplicate_experiment and ntags_ctl2 < ntags_rep2:
                        logger.info("Fewer reads in control replicate 2 than experiment replicate 2.  Using pooled controls for replicate 2.")
                        rep2_control = pooled_controls
                        output.update({'rep2_control': pooled_controls})
                else:
                    logger.info(
                        "Using distinct controls for replicate 1 and 2.")
                    rep1_control = ctl1_ta
                    rep2_control = ctl2_ta
                    output.update({'rep1_control': ctl1_ta,
                                   'rep2_control': ctl2_ta})

    rep1_pr_subjob = pseudoreplicator(**{"input_tags": rep1_ta})
    r1pr1 = rep1_pr_subjob.get('pseudoreplicate1')
    r1pr2 = rep1_pr_subjob.get('pseudoreplicate2')
    output.update({'r1pr1': r1pr1,
                   'r1pr2': r1pr2})

    if not simplicate_experiment:
        rep2_pr_subjob = pseudoreplicator(**{"input_tags": rep2_ta})
        r2pr1 = rep2_pr_subjob.get('pseudoreplicate1')
        r2pr2 = rep2_pr_subjob.get('pseudoreplicate2')
        output.update({'r2pr1': r2pr1,
                       'r2pr2': r2pr2})
        pool_pr1_subjob = pool(
            **{"inputs": [rep1_pr_subjob.get("pseudoreplicate1"),
                          rep2_pr_subjob.get("pseudoreplicate1")],
               "prefix": 'PPR1'})
        pool_pr2_subjob = pool(
            **{"inputs": [rep1_pr_subjob.get("pseudoreplicate2"),
                          rep2_pr_subjob.get("pseudoreplicate2")],
               "prefix": 'PPR2'})
        ppr1 = pool_pr1_subjob.get('pooled')
        ppr2 = pool_pr2_subjob.get('pooled')
        output.update({'ppr1': ppr1,
                       'ppr2': ppr2})
    # should there be an indication of the simplicateness of the
    # experiment in the output json? this could be a good way to
    # direct the next step without putting too much logic into the
    # workflow. ADDED.
    # Turns out Cromwell does not support reading .json. Instead
    # they have read_map function that accepts 2 column TSVs.
    with open('pool_and_pseudoreplicate_outfiles.mapping', 'w') as f:
        for key in output:
            f.write('%s\t%s\n' % (key, output[key]))

    return output


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], parse_true_or_false(sys.argv[3]))
    else:
        main(sys.argv[1], sys.argv[2], parse_true_or_false(sys.argv[3]), sys.argv[4], sys.argv[5], parse_true_or_false(sys.argv[6]))

# this needs to go to other image
'''
    common_args = {
        'chrom_sizes':      chrom_sizes,
        'genomesize':       genomesize,
        'narrowpeak_as':    narrowpeak_as,
        'gappedpeak_as':    gappedpeak_as,
        'broadpeak_as':     broadpeak_as
        }
    # if the fragment_length argument is given, update macs2 input
    if fragment_length is not None:
        common_args.update({'fragment_length' : fragment_length})

    common_args.update({'prefix': 'r1'})
    rep1_peaks_subjob      = macs2( rep1_ta,
                                    rep1_control,
                                    rep1_xcor, **common_args)

    common_args.update({'prefix': 'r1pr1'})
    rep1pr1_peaks_subjob   = macs2( rep1_pr_subjob.get_output_ref("pseudoreplicate1"),
                                    rep1_control,
                                    rep1_xcor, **common_args)

    common_args.update({'prefix': 'r1pr2'})
    rep1pr2_peaks_subjob   = macs2( rep1_pr_subjob.get_output_ref("pseudoreplicate2"),
                                    rep1_control,
                                    rep1_xcor, **common_args)

    if not simplicate_experiment:
        common_args.update({'prefix': 'r2'})
        rep2_peaks_subjob      = macs2( rep2_ta,
                                        rep2_control,
                                        rep2_xcor, **common_args)

        common_args.update({'prefix': 'r2pr1'})
        rep2pr1_peaks_subjob   = macs2( rep2_pr_subjob.get_output_ref("pseudoreplicate1"),
                                        rep2_control,
                                        rep2_xcor, **common_args)

        common_args.update({'prefix': 'r2pr2'})
        rep2pr2_peaks_subjob   = macs2( rep2_pr_subjob.get_output_ref("pseudoreplicate2"),
                                        rep2_control,
                                        rep2_xcor, **common_args)

        common_args.update({'prefix': 'pool'})
        pooled_peaks_subjob    = macs2( pooled_replicates,
                                        control_for_pool,   
                                        pooled_replicates_xcor_subjob.get_output_ref("CC_scores_file"), **common_args)

        common_args.update({'prefix': 'ppr1'})
        pooledpr1_peaks_subjob = macs2( pool_pr1_subjob.get_output_ref("pooled"),
                                        control_for_pool,
                                        pooled_replicates_xcor_subjob.get_output_ref("CC_scores_file"), **common_args)

        common_args.update({'prefix': 'ppr2'})
        pooledpr2_peaks_subjob = macs2( pool_pr2_subjob.get_output_ref("pooled"),
                                        control_for_pool,
                                        pooled_replicates_xcor_subjob.get_output_ref("CC_scores_file"), **common_args)

    output = {
        'rep1_narrowpeaks':         rep1_peaks_subjob.get_output_ref("narrowpeaks"),
        'rep1_gappedpeaks':         rep1_peaks_subjob.get_output_ref("gappedpeaks"),
        'rep1_broadpeaks':          rep1_peaks_subjob.get_output_ref("broadpeaks"),
        'rep1_narrowpeaks_bb':      rep1_peaks_subjob.get_output_ref("narrowpeaks_bb"),
        'rep1_gappedpeaks_bb':      rep1_peaks_subjob.get_output_ref("gappedpeaks_bb"),
        'rep1_broadpeaks_bb':       rep1_peaks_subjob.get_output_ref("broadpeaks_bb"),
        'rep1_fc_signal':           rep1_peaks_subjob.get_output_ref("fc_signal"),
        'rep1_pvalue_signal':       rep1_peaks_subjob.get_output_ref("pvalue_signal"),

        'rep1pr1_narrowpeaks':      rep1pr1_peaks_subjob.get_output_ref("narrowpeaks"),
        'rep1pr1_gappedpeaks':      rep1pr1_peaks_subjob.get_output_ref("gappedpeaks"),
        'rep1pr1_broadpeaks':       rep1pr1_peaks_subjob.get_output_ref("broadpeaks"),
        'rep1pr1_fc_signal':        rep1pr1_peaks_subjob.get_output_ref("fc_signal"),
        'rep1pr1_pvalue_signal':    rep1pr1_peaks_subjob.get_output_ref("pvalue_signal"),

        'rep1pr2_narrowpeaks':      rep1pr2_peaks_subjob.get_output_ref("narrowpeaks"),
        'rep1pr2_gappedpeaks':      rep1pr2_peaks_subjob.get_output_ref("gappedpeaks"),
        'rep1pr2_broadpeaks':       rep1pr2_peaks_subjob.get_output_ref("broadpeaks"),
        'rep1pr2_fc_signal':        rep1pr2_peaks_subjob.get_output_ref("fc_signal"),
        'rep1pr2_pvalue_signal':    rep1pr2_peaks_subjob.get_output_ref("pvalue_signal")
    }

    if not simplicate_experiment:
        output.update({
            'rep2_narrowpeaks':         rep2_peaks_subjob.get_output_ref("narrowpeaks"),
            'rep2_gappedpeaks':         rep2_peaks_subjob.get_output_ref("gappedpeaks"),
            'rep2_broadpeaks':          rep2_peaks_subjob.get_output_ref("broadpeaks"),
            'rep2_narrowpeaks_bb':      rep2_peaks_subjob.get_output_ref("narrowpeaks_bb"),
            'rep2_gappedpeaks_bb':      rep2_peaks_subjob.get_output_ref("gappedpeaks_bb"),
            'rep2_broadpeaks_bb':       rep2_peaks_subjob.get_output_ref("broadpeaks_bb"),
            'rep2_fc_signal':           rep2_peaks_subjob.get_output_ref("fc_signal"),
            'rep2_pvalue_signal':       rep2_peaks_subjob.get_output_ref("pvalue_signal"),

            'rep2pr1_narrowpeaks':      rep2pr1_peaks_subjob.get_output_ref("narrowpeaks"),
            'rep2pr1_gappedpeaks':      rep2pr1_peaks_subjob.get_output_ref("gappedpeaks"),
            'rep2pr1_broadpeaks':       rep2pr1_peaks_subjob.get_output_ref("broadpeaks"),
            'rep2pr1_fc_signal':        rep2pr1_peaks_subjob.get_output_ref("fc_signal"),
            'rep2pr1_pvalue_signal':    rep2pr1_peaks_subjob.get_output_ref("pvalue_signal"),

            'rep2pr2_narrowpeaks':      rep2pr2_peaks_subjob.get_output_ref("narrowpeaks"),
            'rep2pr2_gappedpeaks':      rep2pr2_peaks_subjob.get_output_ref("gappedpeaks"),
            'rep2pr2_broadpeaks':       rep2pr2_peaks_subjob.get_output_ref("broadpeaks"),
            'rep2pr2_fc_signal':        rep2pr2_peaks_subjob.get_output_ref("fc_signal"),
            'rep2pr2_pvalue_signal':    rep2pr2_peaks_subjob.get_output_ref("pvalue_signal"),

            'pooled_narrowpeaks':       pooled_peaks_subjob.get_output_ref("narrowpeaks"),
            'pooled_gappedpeaks':       pooled_peaks_subjob.get_output_ref("gappedpeaks"),
            'pooled_broadpeaks':        pooled_peaks_subjob.get_output_ref("broadpeaks"),
            'pooled_narrowpeaks_bb':    pooled_peaks_subjob.get_output_ref("narrowpeaks_bb"),
            'pooled_gappedpeaks_bb':    pooled_peaks_subjob.get_output_ref("gappedpeaks_bb"),
            'pooled_broadpeaks_bb':     pooled_peaks_subjob.get_output_ref("broadpeaks_bb"),
            'pooled_fc_signal':         pooled_peaks_subjob.get_output_ref("fc_signal"),
            'pooled_pvalue_signal':     pooled_peaks_subjob.get_output_ref("pvalue_signal"),

            'pooledpr1_narrowpeaks':    pooledpr1_peaks_subjob.get_output_ref("narrowpeaks"),
            'pooledpr1_gappedpeaks':    pooledpr1_peaks_subjob.get_output_ref("gappedpeaks"),
            'pooledpr1_broadpeaks':     pooledpr1_peaks_subjob.get_output_ref("broadpeaks"),
            'pooledpr1_fc_signal':      pooledpr1_peaks_subjob.get_output_ref("fc_signal"),
            'pooledpr1_pvalue_signal':  pooledpr1_peaks_subjob.get_output_ref("pvalue_signal"),

            'pooledpr2_narrowpeaks':    pooledpr2_peaks_subjob.get_output_ref("narrowpeaks"),
            'pooledpr2_gappedpeaks':    pooledpr2_peaks_subjob.get_output_ref("gappedpeaks"),
            'pooledpr2_broadpeaks':     pooledpr2_peaks_subjob.get_output_ref("broadpeaks"),
            'pooledpr2_fc_signal':      pooledpr2_peaks_subjob.get_output_ref("fc_signal"),
            'pooledpr2_pvalue_signal':  pooledpr2_peaks_subjob.get_output_ref("pvalue_signal")
        })
'''
