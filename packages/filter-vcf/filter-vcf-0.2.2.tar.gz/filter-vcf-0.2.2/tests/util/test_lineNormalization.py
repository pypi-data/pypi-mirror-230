from unittest import TestCase
from unittest.mock import patch, Mock, call

from filter_vcf.util.lineNormalization import normalize_vcf_line, perform_line_normalization
from tests.utils import FileMock

line = "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"


class TestNormalizeVCFLine(TestCase):
    @patch("filter_vcf.util.lineNormalization.filter_line", return_value=line)
    @patch("filter_vcf.util.lineNormalization.add_depth_to_line", return_value=line)
    @patch("filter_vcf.util.lineNormalization.filter_non_ref_from_line", return_value=line)
    @patch("filter_vcf.util.lineNormalization.keep_unique_line", return_value=line)
    def test_normalize_vcf_line(
        self,
        mock_keep_unique_line: Mock,
        mock_filter_non_ref_from_line: Mock,
        mock_add_depth_to_line: Mock,
        mock_filter_line: Mock,
    ):
        result = normalize_vcf_line(line, None, {"filters": "PASS", "depth": True, "unique": True})

        self.assertEqual(result, f"{line}\n")
        mock_filter_line.assert_called_once_with(line, "PASS")
        mock_add_depth_to_line.assert_called_once_with(line)
        mock_filter_non_ref_from_line.assert_called_once_with(line)
        mock_keep_unique_line.assert_called_once_with(line, None)

    @patch("filter_vcf.util.lineNormalization.filter_line", return_value=None)
    @patch("filter_vcf.util.lineNormalization.add_depth_to_line", return_value=None)
    @patch("filter_vcf.util.lineNormalization.filter_non_ref_from_line", return_value=None)
    @patch("filter_vcf.util.lineNormalization.keep_unique_line", return_value=None)
    def test_normalize_vcf_line_with_none(self, *_):
        result = normalize_vcf_line("", None, {"filters": "PASS", "depth": True, "unique": True})

        self.assertEqual(result, None)


test_data = [
    "# header line",
    "variant line",
]


class TestPerformLineNormalization(TestCase):
    @patch("filter_vcf.util.lineNormalization.normalize_vcf_line", return_value="variant line")
    @patch("os.rename")
    @patch("gzip.open")
    def test_perform_line_normalization(
        self,
        mock_gzip_open: Mock,
        mock_rename: Mock,
        mock_normalize_vcf_line: Mock,
    ):
        mock_write = Mock()
        mock_gzip_open.return_value.__enter__.return_value = FileMock(test_data, mock_write)

        perform_line_normalization("in.vcf", "/tmp", {"filters": "PASS", "depth": True})

        mock_rename.assert_called_once_with("in.vcf", "/tmp/working.vcf.gz")
        mock_gzip_open.assert_any_call("/tmp/working.vcf.gz", "rt")
        mock_gzip_open.assert_any_call("in.vcf", "wt")
        mock_normalize_vcf_line.assert_called_once_with(
            "variant line", None, {"filters": "PASS", "depth": True}
        )
        mock_write.assert_has_calls([call("# header line"), call("variant line")])
