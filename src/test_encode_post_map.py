import unittest
import encode_post_map


class TestEncodePostMap(unittest.TestCase):

    def setUp(self):
        pass

    def test_strip_extensions(self):
        STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '.fa', '.fasta']
        self.assertEquals(encode_post_map.strip_extensions('fn.gz', STRIP_EXTENSIONS), 'fn')
        self.assertEquals(encode_post_map.strip_extensions('', STRIP_EXTENSIONS), '')
        self.assertEquals(encode_post_map.strip_extensions(
            'no.extensions.here', STRIP_EXTENSIONS), 'no.extensions.here')
        # if the first part is falsy in basename = basename.rpartition(extension)[0] or basename
        # do nothing
        self.assertEquals(encode_post_map.strip_extensions('.gz.somename', STRIP_EXTENSIONS),
                          '.gz.somename')

    def test_resolve_reference(self):
        pass

    def test_flagstat_parse(self):
        pass

    def test_special_sort(self):
        pass

    def test_figure_out_sort(self):
        pass

    def test_postprocess(self):
        pass


if __name__ == "__main__":
    unittest.main()
