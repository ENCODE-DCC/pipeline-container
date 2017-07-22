import json
import hashlib
import glob
import sys
from pprint import pprint

KNOWN_OUTPUT_VALUES = {
    'crop_length': 'native',
    'paired_end': False,
    'n_mapped_reads': 159120, # 30274746
    'n_filtered_mapped_reads': 159120, # 21871835
    'PBC1': '1.000000', # 0.952926
    'PBC2': 'inf', # 21.819143
    'NRF': '1.000000', # 0.951122
    'duplicate_fraction': '0', # 0.0513
    'NSC': 1.37277, # 1.237846
    'RSC': 2.010693, # 1.994183
    'est_frag_len': 120 # 125
}

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
    path_to_output_folder = sys.argv[1]

    mapping_output_json = 'mapping.json'
    post_mapping_output_json = 'post_mapping.json'
    filter_output_json = 'filter_qc.json'
    xcor_output_json = 'xcor.json'

    mapping_dict = {}
    post_mapping_dict = {}
    filter_dict = {}
    xcor_dict = {}

    with open(sys.argv[1]+'/' + mapping_output_json) as data:
        mapping_dict = json.load(data)
    with open(sys.argv[1]+'/' + post_mapping_output_json) as data:
        post_mapping_dict = json.load(data)
    with open(sys.argv[1]+'/' + filter_output_json) as data:
        filter_dict = json.load(data)
    with open(sys.argv[1]+'/' + xcor_output_json) as data:
        xcor_dict = json.load(data)

    result_dict = {'steps': {}, 'overall': True, 'messages': ''}

    keep_examination = True
    if not mapping_dict:
        result_dict['steps']['mapping_step'] = False
        result_dict['messages'] += 'No output from mapping step was found. '
        keep_examination = False
    if not post_mapping_dict:
        result_dict['steps']['post_mapping_step'] = False
        result_dict['messages'] += 'No output from post-mapping step was found. '
        keep_examination = False
    if not filter_dict:
        result_dict['steps']['filtering_step'] = False
        result_dict['messages'] += 'No output from filtering step was found. '
        keep_examination = False
    if not xcor_dict:
        result_dict['steps']['xcor_step'] = False
        result_dict['messages'] += 'No output from xcor step was found. '
        keep_examination = False
    

    if not keep_examination:
        result_dict['overall'] = False
        with open('results.json', 'w') as f:
            json.dump(result_dict, f)
    else:
        result_dict['steps']['mapping_step'] = {}
        result_dict['steps']['post_mapping_step'] = {}
        result_dict['steps']['filtering_step'] = {}
        result_dict['steps']['xcor_step'] = {}
        
        if mapping_dict.get('crop_length') == KNOWN_OUTPUT_VALUES['crop_length']:
            result_dict['steps']['mapping_step']['crop_length'] = True
        else:
            result_dict['messages'] += 'The crop length reported \'{}\', '.format(mapping_dict.get('crop_length')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['crop_length'])
            result_dict['overall'] = False
        
        if mapping_dict.get('paired_end') == KNOWN_OUTPUT_VALUES['paired_end']:
            result_dict['steps']['mapping_step']['paired_end'] = True
        else:
            result_dict['messages'] += 'Reported paired end boolean \'{}\' '.format(mapping_dict.get('paired_end')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['paired_end'])
            result_dict['overall'] = False

        if post_mapping_dict.get('n_mapped_reads') == KNOWN_OUTPUT_VALUES['n_mapped_reads']:
            result_dict['steps']['post_mapping_step']['n_mapped_reads'] = True
        else:
            result_dict['messages'] += 'Reported number of mapped reads \'{}\' '.format(mapping_dict.get('n_mapped_reads')) + \
                                       'is different from the expected number of mapped reads \'{}\'. '.format(KNOWN_OUTPUT_VALUES['n_mapped_reads'])
            result_dict['overall'] = False

        if filter_dict.get('PBC1') == KNOWN_OUTPUT_VALUES['PBC1']:
            result_dict['steps']['filtering_step']['PBC1'] = True
        else:
            result_dict['messages'] += 'Reported PCR Bottlenecking Coefficient 1 \'{}\' '.format(mapping_dict.get('PBC1')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['PBC1'])
            result_dict['overall'] = False
        if filter_dict.get('PBC2') == KNOWN_OUTPUT_VALUES['PBC2']:
            result_dict['steps']['filtering_step']['PBC2'] = True
        else:
            result_dict['messages'] += 'Reported PCR Bottlenecking Coefficient 2 \'{}\' '.format(mapping_dict.get('PBC2')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['PBC2'])
            result_dict['overall'] = False
        if filter_dict.get('NRF') == KNOWN_OUTPUT_VALUES['NRF']:
            result_dict['steps']['filtering_step']['NRF'] = True
        else:
            result_dict['messages'] += 'Reported Non-Redindant Fraction \'{}\' '.format(mapping_dict.get('NRF')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['NRF'])
            result_dict['overall'] = False
        if filter_dict.get('n_filtered_mapped_reads') == KNOWN_OUTPUT_VALUES['n_filtered_mapped_reads']:
            result_dict['steps']['filtering_step']['n_filtered_mapped_reads'] = True
        else:
            result_dict['messages'] += 'Reported number of filtered mapped reads \'{}\' '.format(mapping_dict.get('n_filtered_mapped_reads')) + \
                                       'is different from the expected number of filtered mapped reads \'{}\'. '.format(KNOWN_OUTPUT_VALUES['n_filtered_mapped_reads'])
            result_dict['overall'] = False
        
        
        if filter_dict.get('duplicate_fraction') == KNOWN_OUTPUT_VALUES['duplicate_fraction']:
            result_dict['steps']['filtering_step']['duplicate_fraction'] = True
        else:
            result_dict['messages'] += 'Reported duplicate fraction \'{}\' '.format(mapping_dict.get('duplicate_fraction')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['duplicate_fraction'])
            result_dict['overall'] = False


        if xcor_dict.get('NSC') == KNOWN_OUTPUT_VALUES['NSC']:
            result_dict['steps']['xcor_step']['NSC'] = True
        else:
            result_dict['messages'] += 'Reported Normalized Strand Cross-correlation coefficient \'{}\' '.format(mapping_dict.get('est_frag_len')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['est_frag_len'])
            result_dict['overall'] = False        
        if xcor_dict.get('RSC') == KNOWN_OUTPUT_VALUES['RSC']:
            result_dict['steps']['xcor_step']['RSC'] = True
        else:
            result_dict['messages'] += 'Reported Relative Strand Cross-correlation coefficient \'{}\' '.format(mapping_dict.get('est_frag_len')) + \
                                       'is different from the expected value of \'{}\'. '.format(KNOWN_OUTPUT_VALUES['est_frag_len'])
            result_dict['overall'] = False 
        if xcor_dict.get('est_frag_len') == KNOWN_OUTPUT_VALUES['est_frag_len']:
            result_dict['steps']['xcor_step']['est_frag_len'] = True
        else:
            result_dict['messages'] += 'Reported extimated fragment length \'{}\' '.format(mapping_dict.get('est_frag_len')) + \
                                       'is different from the expected estimated fragment length \'{}\'. '.format(KNOWN_OUTPUT_VALUES['est_frag_len'])
            result_dict['overall'] = False

    with open('results.json', 'w') as f:
        json.dump(result_dict, f)
    pprint(result_dict)

if __name__ == "__main__":
    main()