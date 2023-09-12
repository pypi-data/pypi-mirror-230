from unittest import TestCase

from filter_vcf.util.removeNonRef import filter_non_ref_from_line


class TestFilterNonRefFromLine(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(filter_non_ref_from_line(line), None)

    def test_returns_none_for_non_ref_line(self):
        line = "chrX	154766321	rs2728532	G	<NON_REF>	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84"
        self.assertEqual(filter_non_ref_from_line(line), None)

    def test_returns_line_for_non_non_ref_line(self):
        line = "chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84"
        self.assertEqual(filter_non_ref_from_line(line), line)
