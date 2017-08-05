import unittest
import common
from mock import patch, mock_open


def give_fhs(x):
    if x == 'correct':
        return mock_open(read_data='1 2 3')
    else:
        return mock_open(read_data='a b c')


class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def test_test(self):
        pass

    def test_flat(self):
        # if input is not iterable, raise TypeError
        self.assertRaises(TypeError, common.flat, 1)
        # empties stay empty
        self.assertEquals(common.flat(''), [])
        self.assertEquals(common.flat([]), [])
        # strings get split
        self.assertEquals(common.flat('test'), ['t', 'e', 's', 't'])
        # flat lists stay flat
        self.assertEquals(common.flat(['a', 'ab']), ['a', 'ab'])
        # nested iterables become flat lists
        self.assertEquals(common.flat(['a', ('b', 'c')]), ['a', 'b', 'c'])

    def test_rstrips(self):
        # empty does not strip anything
        self.assertEquals(common.rstrips('abc', ''), 'abc')
        # stripping with the same string returns empty
        a = 'abc'
        self.assertEquals(common.rstrips(a, a), '')
        # match strips
        self.assertEquals(common.rstrips('abcd', 'cd'), 'ab')
        # non-match does not strip
        self.assertEquals(common.rstrips('abcd', 'dc'), 'abcd')

    def test_touch(self):
        pass

    def test_block_on(self):
        pass

    def test_run_pipe(self):
        pass

    def test_uncompress(self):
        pass

    def test_compress(self):
        pass

    def test_count_lines(self):
        pass

    def test_xcor_fraglen(self):
        with patch('common.open', mock_open(read_data='1 2')) as _:
            self.assertRaises(IndexError, common.xcor_fraglen, 'foo')
        with patch('common.open', mock_open(read_data='1 2 3')) as _:
            self.assertEquals(common.xcor_fraglen('foo'), 3)
        with patch('common.open', mock_open(read_data='1 2 c')) as _:
            self.assertRaises(ValueError, common.xcor_fraglen, 'foo')

    def test_frip(self):
        pass

    def test_bed2bb(self):
        pass

    def test_rescale_scores(self):
        pass

    def test_slop_clip(self):
        pass

    def test_processkey(self):
        pass

    def test_encoded_get(self):
        pass

    def test_encoded_update(self):
        pass

    def test_encoded_patch(self):
        pass

    def test_encoded_post(self):
        pass

    def test_encoded_put(self):
        pass

    def test_pprint_json(self):
        pass

    def test_merge_dicts(self):
        pass

    def test_md5(self):
        pass

    def test_after(self):
        pass

    def test_biorep_ns(self):
        pass

    def test_derived_from_references_generator(self):
        pass

    def test_derived_from_references(self):
        pass

    def test_expired(self):
        pass


if __name__ == "__main__":
    unittest.main()