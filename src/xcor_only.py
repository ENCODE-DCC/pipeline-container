from multiprocessing import cpu_count
import common
import logging
import sys
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

SPP_TOOL_PATH = '/'.join(
    [os.getenv('PHANTOMPEAKQUALTOOLS_HOME', '.'), "run_spp.R"])


def parse_true_or_false(argument):
    return argument.lower() == 'true'


def xcor_parse(fname):
    with open(fname, 'r') as xcor_file:
        if not xcor_file:
            return None

        lines = xcor_file.read().splitlines()
        line = lines[0].rstrip('\n')
        # CC_SCORE FILE format:
        #   Filename <tab>
        #   numReads <tab>
        #   estFragLen <tab>
        #   corr_estFragLen <tab>
        #   PhantomPeak <tab>
        #   corr_phantomPeak <tab>
        #   argmin_corr <tab>
        #   min_corr <tab>
        #   phantomPeakCoef <tab>
        #   relPhantomPeakCoef <tab>
        #   QualityTag

        headers = [
            'Filename', 'numReads', 'estFragLen', 'corr_estFragLen',
            'PhantomPeak', 'corr_phantomPeak', 'argmin_corr', 'min_corr',
            'phantomPeakCoef', 'relPhantomPeakCoef', 'QualityTag'
        ]
        metrics = line.split('\t')
        headers.pop(0)
        metrics.pop(0)

        xcor_qc = dict(zip(headers, metrics))
    return xcor_qc


def main(input_tagAlign, paired_end):

    input_tagAlign_filename = input_tagAlign
    input_tagAlign_basename = input_tagAlign_filename.rstrip('.gz')

    uncompressed_TA_filename = input_tagAlign_basename
    out, err = common.run_pipe(['gzip -d %s' % (input_tagAlign_filename)])

    # =================================
    # Subsample tagAlign file
    # ================================
    NREADS = 15000000
    if paired_end:
        end_infix = 'MATE1'
    else:
        end_infix = 'SE'
    subsampled_TA_filename = \
        input_tagAlign_basename + \
        ".sample.%d.%s.tagAlign.gz" % (NREADS/1000000, end_infix)
    steps = [
        'grep -v "chrM" %s' % (uncompressed_TA_filename),
        'shuf -n %d --random-source=%s' % (NREADS, uncompressed_TA_filename)
    ]
    if paired_end:
        steps.extend([r"""awk 'BEGIN{OFS="\t"}{$4="N";$5="1000";print $0}'"""])
    steps.extend(['gzip -cn'])
    out, err = common.run_pipe(steps, outfile=os.path.basename(subsampled_TA_filename))

    # Calculate Cross-correlation QC scores
    CC_scores_filename = subsampled_TA_filename + ".cc.qc"
    CC_plot_filename = subsampled_TA_filename + ".cc.plot.pdf"

    # CC_SCORE FILE format
    # Filename <tab>
    # numReads <tab>
    # estFragLen <tab>
    # corr_estFragLen <tab>
    # PhantomPeak <tab>
    # corr_phantomPeak <tab>
    # argmin_corr <tab>
    # min_corr <tab>
    # phantomPeakCoef <tab>
    # relPhantomPeakCoef <tab>
    # QualityTag

    # spp will be installed in the docker container, so this is not needed
    # subprocess.check_output(shlex.split('R CMD INSTALL %s' % (spp_tarball)))
    # run spp
    # refer cwd for testing
    # does this really have to be with _no_dups
    run_spp_command = SPP_TOOL_PATH
    out, err = common.run_pipe([
        "Rscript %s -c=%s -p=%d -filtchr=chrM -savp=%s -out=%s" %
        (run_spp_command, subsampled_TA_filename, cpu_count(),
         CC_plot_filename, CC_scores_filename)
    ])
    out, err = common.run_pipe(
        [r"""sed -r  's/,[^\t]+//g' %s""" % (CC_scores_filename)],
        outfile="temp")
    out, err = common.run_pipe(["mv temp %s" % (CC_scores_filename)])

    xcor_qc = xcor_parse(CC_scores_filename)

    # Return the outputs
    output = {
        "CC_scores_file": CC_scores_filename,
        "CC_plot_file": CC_plot_filename,
        "paired_end": paired_end,
        "RSC": float(xcor_qc.get('relPhantomPeakCoef')),
        "NSC": float(xcor_qc.get('phantomPeakCoef')),
        "est_frag_len": float(xcor_qc.get('estFragLen'))
    }

    return output


if __name__ == '__main__':
    main(sys.argv[1], parse_true_or_false(sys.argv[2]))
