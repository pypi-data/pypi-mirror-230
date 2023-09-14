from unittest import TestCase
from unittest.mock import patch, Mock

from filter_vcf.util.detectVcf import detect_vcf
from tests.utils import FileMock

chr_file_lines = [
    "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO",
    "chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827",
]

num_file_lines = [
    "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO",
    "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827",
]


@patch("gzip.open")
class TestDetectVCF(TestCase):
    def test_detect_vcf_chr(self, mock_open: Mock):
        mock_open.return_value.__enter__.return_value = FileMock(chr_file_lines)

        result = detect_vcf("in.vcf.gz")

        self.assertEqual(result, "chr")
        mock_open.assert_any_call("in.vcf.gz", "rt")

    def test_detect_vcf_num(self, mock_open: Mock):
        mock_open.return_value.__enter__.return_value = FileMock(num_file_lines)

        result = detect_vcf("in.vcf.gz")

        self.assertEqual(result, "num")
