import json
import hashlib
import glob
import sys

KNOWN_FILES_MD5 = {
    'rep1_ENCFF000VOL_chr21.raw.srt.bam.flagstat.qc':
        '13557cf731440268fc780bb0f17bb8ba',
    'rep1_ENCFF000VOL_chr21.raw.srt.filt.nodup.srt.final.pbc.qc':
        'fffb748b255a44f00c79c9a676575420',
    'rep1_ENCFF000VOL_chr21.raw.srt.filt.nodup.srt.final.flagstat.qc':
        '13557cf731440268fc780bb0f17bb8ba',
    'rep1_ENCFF000VOL_chr21.raw.srt.filt.nodup.srt.final.filt.nodup.sample.15.SE.tagAlign.gz.cc.qc':
        '9b373f2d5bb5a73cb74b24cf4f9bb132',
    'rep1_ENCFF000VOL_chr21.raw.srt.dup.qc':
        'eef880e26bbae594766e32e470a7d01e'}


def calculatemd5FromFile(filepath, chunksize=4096):
    '''calculate md5sum of a file in filepath.
        do the calculation in chunks of 4096
        bytes as a memory efficiency consideration.'''
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        # Iter is calling f.read(chunksize) until it returns
        # the sentinel b''(empty bytes)
        for chunk in iter(lambda: f.read(chunksize), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    output_md5 = dict()
    for filepath in glob.glob(sys.argv[1]+'/*.qc'):
        filename = filepath.strip().split('/')[-1]
        print (filename)
        if filename in KNOWN_FILES_MD5:
            output_md5[filename] = calculatemd5FromFile(filepath)

    result = {key: 'Match' if
                   output_md5[key] == KNOWN_FILES_MD5[key] else
                   'Not match' for key in output_md5}
    overall = all(
        [output_md5[key] == KNOWN_FILES_MD5[key] for key in output_md5])

    pass_status = 'PASS' if overall and output_md5 else 'FAIL'
    result['Overall'] = pass_status
    with open('results.json', 'w') as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()