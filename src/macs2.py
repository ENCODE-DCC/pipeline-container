#!/usr/bin/env python
# macs2 0.0.1

import os
import common
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def main(experiment,
         control,
         xcor_scores_input,
         chrom_sizes,
         narrowpeak_as,
         gappedpeak_as,
         broadpeak_as,
         genomesize,
         prefix=None,
         fragment_length=None):

    narrowPeak_as = narrowpeak_as
    gappedPeak_as = gappedpeak_as
    broadPeak_as = broadpeak_as

    # Define the output filenames

    if not prefix:
        prefix = experiment
    if prefix.endswith('.gz'):
        prefix = prefix[:-3]

    narrowPeak_fn = "%s.narrowPeak" % prefix
    gappedPeak_fn = "%s.gappedPeak" % prefix
    broadPeak_fn = "%s.broadPeak" % prefix
    narrowPeak_gz_fn = narrowPeak_fn + ".gz"
    gappedPeak_gz_fn = gappedPeak_fn + ".gz"
    broadPeak_gz_fn = broadPeak_fn + ".gz"
    fc_signal_fn = "%s.fc_signal.bw" % prefix
    pvalue_signal_fn = "%s.pvalue_signal.bw" % prefix

    # Extract the fragment length estimate from column 3 of the
    # cross-correlation scores file
    # if the fragment_length argument is given, use that instead
    if fragment_length is not None:
        fraglen = str(fragment_length)
        logger.info("User given fragment length %s" % fraglen)
    else:
        with open(xcor_scores_input, 'r') as fh:
            firstline = fh.readline()
            fraglen = firstline.split()[2]  # third column
            logger.info("Fraglen %s" % (fraglen))

    # ===========================================
    # Generate narrow peaks and preliminary signal tracks
    # ============================================

    command = 'macs2 callpeak ' + \
              '-t %s -c %s ' % (experiment, control) + \
              '-f BED -n %s ' % prefix + \
              '-g %s -p 1e-2 --nomodel --shift 0 --extsize %s --keep-dup all -B --SPMR' % (genomesize, fraglen)
    logger.info(command)
    returncode = common.block_on(command)
    logger.info("MACS2 exited with returncode %d" % (returncode))
    assert returncode == 0, "MACS2 non-zero return"

    # MACS2 sometimes calls features off the end of chromosomes.  Fix that.
    clipped_narrowpeak_fn = common.slop_clip(
        '%s_peaks.narrowPeak' % prefix, chrom_sizes)

    # Rescale Col5 scores to range 10-1000 to conform to narrowPeak.as format
    # (score must be <1000)
    rescaled_narrowpeak_fn = common.rescale_scores(
        clipped_narrowpeak_fn, scores_col=5)

    # Sort by Col8 in descending order and replace long peak names in Column 4
    # with Peak_<peakRank>
    pipe = [
        'sort -k 8gr,8gr %s' % (rescaled_narrowpeak_fn),
        r"""awk 'BEGIN{OFS="\t"}{$4="Peak_"NR ; print $0}'""",
        'tee %s' % (narrowPeak_fn), 'gzip -cn'
    ]
    out, err = common.run_pipe(pipe, '%s' % (narrowPeak_gz_fn))

    # remove additional files
    # rm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_peaks.xls ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_peaks.bed ${peakFile}_summits.bed

    # ===========================================
    # Generate Broad and Gapped Peaks
    # ============================================

    command = 'macs2 callpeak ' + \
              '-t %s -c %s ' % (experiment, control) + \
              '-f BED -n %s ' % prefix + \
              '-g %s -p 1e-2 --broad --nomodel --shift 0 --extsize %s --keep-dup all' % (genomesize, fraglen)
    logger.info(command)
    returncode = common.block_on(command)
    logger.info("MACS2 exited with returncode %d" % (returncode))
    assert returncode == 0, "MACS2 non-zero return"

    # MACS2 sometimes calls features off the end of chromosomes.  Fix that.
    clipped_broadpeak_fn = common.slop_clip(
        '%s_peaks.broadPeak' % prefix, chrom_sizes)

    # Rescale Col5 scores to range 10-1000 to conform to narrowPeak.as format
    # (score must be <1000)
    rescaled_broadpeak_fn = common.rescale_scores(
        clipped_broadpeak_fn, scores_col=5)

    # Sort by Col8 (for broadPeak) or Col 14(for gappedPeak) in descending
    # order and replace long peak names in Column 4 with Peak_<peakRank>
    pipe = [
        'sort -k 8gr,8gr %s' % (rescaled_broadpeak_fn),
        r"""awk 'BEGIN{OFS="\t"}{$4="Peak_"NR ; print $0}'""",
        'tee %s' % (broadPeak_fn), 'gzip -cn'
    ]
    out, err = common.run_pipe(pipe, '%s' % (broadPeak_gz_fn))

    # MACS2 sometimes calls features off the end of chromosomes.  Fix that.
    clipped_gappedpeaks_fn = common.slop_clip(
        '%s_peaks.gappedPeak' % prefix,
        chrom_sizes,
        bed_type='gappedPeak')

    # Rescale Col5 scores to range 10-1000 to conform to narrowPeak.as format
    # (score must be <1000)
    rescaled_gappedpeak_fn = common.rescale_scores(
        clipped_gappedpeaks_fn, scores_col=5)

    pipe = [
        'sort -k 14gr,14gr %s' % (rescaled_gappedpeak_fn),
        r"""awk 'BEGIN{OFS="\t"}{$4="Peak_"NR ; print $0}'""",
        'tee %s' % (gappedPeak_fn), 'gzip -cn'
    ]
    out, err = common.run_pipe(pipe, '%s' % (gappedPeak_gz_fn))

    # remove additional files
    # rm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_peaks.xls ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_peaks.bed ${peakFile}_summits.bed

    # ===========================================
    # For Fold enrichment signal tracks
    # ============================================

    # This file is a tab delimited file with 2 columns Col1 (chromosome name),
    # Col2 (chromosome size in bp).
    command = 'macs2 bdgcmp ' + \
              '-t %s_treat_pileup.bdg ' % prefix + \
              '-c %s_control_lambda.bdg ' % prefix + \
              '-o %s_FE.bdg ' % prefix + \
              '-m FE'
    logger.info(command)
    returncode = common.block_on(command)
    logger.info("MACS2 exited with returncode %d" % (returncode))
    assert returncode == 0, "MACS2 non-zero return"

    # Remove coordinates outside chromosome sizes (stupid MACS2 bug)
    pipe = [
        'slopBed -i %s_FE.bdg -g %s -b 0' % (prefix, chrom_sizes),
        'bedClip stdin %s %s.fc.signal.bedgraph' % (chrom_sizes, prefix)
    ]
    out, err = common.run_pipe(pipe)

    # rm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_FE.bdg

    # Convert bedgraph to bigwig
    command = 'bedGraphToBigWig ' + \
              '%s.fc.signal.bedgraph ' % prefix + \
              '%s ' % (chrom_sizes) + \
              '%s' % (fc_signal_fn)
    logger.info(command)
    returncode = common.block_on(command)
    logger.info("bedGraphToBigWig exited with returncode %d" % (returncode))
    assert returncode == 0, "bedGraphToBigWig non-zero return"
    # drm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}.fc.signal.bedgraph

    # ===========================================
    # For -log10(p-value) signal tracks
    # ============================================

    # Compute sval =
    # min(no. of reads in ChIP, no. of reads in control) / 1,000,000
    out, err = common.run_pipe(['gzip -dc %s' % (experiment), 'wc -l'])
    chipReads = out.strip()
    out, err = common.run_pipe(['gzip -dc %s' % (control), 'wc -l'])
    controlReads = out.strip()
    sval = str(min(float(chipReads), float(controlReads)) / 1000000)

    logger.info("chipReads = %s, controlReads = %s, sval = %s" %
                (chipReads, controlReads, sval))
    returncode = common.block_on(
        'macs2 bdgcmp ' + '-t %s_treat_pileup.bdg ' % prefix +
        '-c %s_control_lambda.bdg ' % prefix +
        '-o %s_ppois.bdg ' % prefix +
        '-m ppois -S %s' % (sval))
    logger.info("MACS2 exited with returncode %d" % (returncode))
    assert returncode == 0, "MACS2 non-zero return"

    # Remove coordinates outside chromosome sizes (stupid MACS2 bug)
    pipe = [
        'slopBed -i %s_ppois.bdg -g %s -b 0' % (prefix, chrom_sizes),
        'bedClip stdin %s %s.pval.signal.bedgraph' % (chrom_sizes, prefix)
    ]
    out, err = common.run_pipe(pipe)

    # rm -rf ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_ppois.bdg

    # Convert bedgraph to bigwig
    command = 'bedGraphToBigWig ' + \
              '%s.pval.signal.bedgraph ' % prefix + \
              '%s ' % (chrom_sizes) + \
              '%s' % (pvalue_signal_fn)
    logger.info(command)
    returncode = common.block_on(command)
    logger.info("bedGraphToBigWig exited with returncode %d" % (returncode))
    assert returncode == 0, "bedGraphToBigWig non-zero return"

    # rm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}.pval.signal.bedgraph
    # rm -f ${PEAK_OUTPUT_DIR}/${CHIP_TA_PREFIX}_treat_pileup.bdg ${peakFile}_control_lambda.bdg

    # ===========================================
    # Generate bigWigs from beds to support trackhub visualization of peak files
    # ============================================

    narrowPeak_bb_fname = common.bed2bb(
        '%s' % (narrowPeak_fn), chrom_sizes, narrowPeak_as, bed_type='bed6+4')
    gappedPeak_bb_fname = common.bed2bb(
        '%s' % (gappedPeak_fn), chrom_sizes, gappedPeak_as, bed_type='bed12+3')
    broadPeak_bb_fname = common.bed2bb(
        '%s' % (broadPeak_fn), chrom_sizes, broadPeak_as, bed_type='bed6+3')

    # Temporary during development to create empty files just to get the applet
    # to exit
    # narrowPeak_bb_fn = "%s.bb" % (narrowPeak_fn)
    # gappedPeak_bb_fn = "%s.bb" % (gappedPeak_fn)
    # broadPeak_bb_fn  = "%s.bb" % (broadPeak_fn)

    output = {
        "narrowpeaks": narrowPeak_gz_fn,
        "gappedpeaks": gappedPeak_gz_fn,
        "broadpeaks": broadPeak_gz_fn,
        "narrowpeaks_bb": narrowPeak_bb_fname,
        "gappedpeaks_bb": gappedPeak_bb_fname,
        "broadpeaks_bb": broadPeak_bb_fname,
        "fc_signal": fc_signal_fn,
        "pvalue_signal": pvalue_signal_fn
    }

    return output


if __name__ == '__main__':
    main(*sys.argv[1:])
