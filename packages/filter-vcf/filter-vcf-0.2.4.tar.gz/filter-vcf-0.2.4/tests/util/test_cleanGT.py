from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.cleanGT import clean_gt, fix_gt_extra, remove_gt_dot


class TestRemoveGTDot(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(remove_gt_dot(line), None)

    def test_does_not_modify_line_with_2_gt_values(self):
        line = "chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84"
        self.assertEqual(remove_gt_dot(line), line)

    def test_does_not_modify_line_with_more_than_2_dot(self):
        line = "chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././.:146:0,10,62,84"
        self.assertEqual(remove_gt_dot(line), line)

    def test_removes_dot_from_gt_field(self):
        line = "chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././3:146:0,10,62,84"
        expected = "chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84"
        self.assertEqual(remove_gt_dot(line), expected)


class TestFixGTExtra(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(fix_gt_extra(line), None)

    def test_does_not_modify_line_with_2_gt_values(self):
        line = "chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84"
        self.assertEqual(fix_gt_extra(line), line)

    def test_keeps_gt_with_2_values(self):
        line = "chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84"
        expected = "chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84"
        self.assertEqual(fix_gt_extra(line), expected)


line = "chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84"


class TestCleanGT(TestCase):
    @patch("filter_vcf.util.cleanGT.fix_gt_extra", return_value=line)
    @patch("filter_vcf.util.cleanGT.remove_gt_dot", return_value=line)
    def test_clean_gt(self, mock_remove_gt_dot, mock_fix_gt_extra):
        self.assertEqual(clean_gt(line), line)
        mock_remove_gt_dot.assert_called_once_with(line)
        mock_fix_gt_extra.assert_called_once_with(line)
