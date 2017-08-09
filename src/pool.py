#!/usr/bin/env python
# pool 0.0.1

from os.path import splitext
import common
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

# inputs are files of gzip format


def main(inputs, prefix=None):

    input_filenames = inputs

    # uses last extension - presumably they are all the same
    extension = splitext(splitext(input_filenames[-1])[0])[1]
    if prefix:
        pooled_filename = prefix + "_pooled%s.gz" % (extension)
    else:
        pooled_filename = \
            '-'.join([splitext(splitext(fn)[0])[0] for fn in input_filenames]) + "_pooled%s.gz" % (extension)
    out, err = common.run_pipe([
        'gzip -dc %s' % (' '.join(input_filenames)),
        'gzip -cn'],
        outfile=pooled_filename)

    output = {
        "pooled": pooled_filename
    }

    return output


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1:3])
    else:
        main(sys.argv[1:3], prefix=sys.argv[3])
