from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.decompose import decompose
from tests.utils import FileMock

line = "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"

logger = Mock()


class TestDecompose(TestCase):
    @patch("subprocess.run")
    @patch("gzip.open")
    @patch("filter_vcf.util.decompose.clean_ad", side_effect=[line, None])
    @patch("filter_vcf.util.decompose.clean_gt", side_effect=[line, None])
    @patch("builtins.open")
    def test_decompose(
        self,
        mock_open,
        mock_clean_gt,
        mock_clean_ad,
        mock_gzip_open,
        mock_subprocess,
    ):
        mock_write = Mock()
        mock_gzip_open.return_value.__enter__.return_value = FileMock(
            write_mock=mock_write,
        )
        mock_open.return_value.__enter__.return_value = FileMock(
            ["#header", line, None],
        )

        decompose("in.vcf.gz", "tmp_dir", logger)

        mock_subprocess.assert_has_calls(
            [
                call(
                    "vt decompose -s in.vcf.gz -o tmp_dir/decomposed.vcf",
                    shell=True,
                    check=True,
                ),
                call(
                    "bcftools view -Oz -o in.vcf.gz in.vcf.gz.tmp",
                    shell=True,
                    check=True,
                ),
            ]
        )
        mock_clean_ad.assert_has_calls([call(line), call(None)])
        mock_clean_gt.assert_has_calls([call(line), call(None)])
        mock_open.assert_any_call("tmp_dir/decomposed.vcf", "rt")
        mock_gzip_open.assert_any_call("in.vcf.gz.tmp", "wt")
        mock_write.assert_has_calls([call("#header"), call(line)])
