from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.convertChrName import convert_chr_name
from tests.utils import FileMock


@patch("subprocess.run")
@patch("os.remove")
@patch("gzip.open")
class TestConvertChrName(TestCase):
    def test_convert_chr_name_chr(
        self, mock_gzip_open: Mock, mock_remove: Mock, mock_subprocess: Mock
    ):
        test_data = [
            "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO",
            "",
            "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827",
            "MT	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897",
        ]
        mock_write = Mock()
        mock_gzip_open.return_value.__enter__.return_value = FileMock(test_data, mock_write)

        convert_chr_name("in.vcf.gz", "chr")

        mock_remove.assert_called_once_with("in.vcf.gz")
        mock_subprocess.assert_called_once_with(
            "bcftools view -Oz -o in.vcf.gz in.vcf.gz.tmp", shell=True, check=True
        )
        mock_gzip_open.assert_any_call("in.vcf.gz", "rt")
        mock_gzip_open.assert_any_call("in.vcf.gz.tmp", "wt")
        mock_write.assert_has_calls(
            [
                call("#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO"),
                call(
                    "chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"
                ),
                call(
                    "chrM	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897"
                ),
            ]
        )

    def test_convert_chr_name_num(self, mock_gzip_open: Mock, *_):
        test_data = [
            "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO",
            "chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827",
            "chrM	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897",
        ]
        mock_write = Mock()
        mock_gzip_open.return_value.__enter__.return_value = FileMock(test_data, mock_write)

        convert_chr_name("in.vcf.gz", "num")

        mock_write.assert_has_calls(
            [
                call("#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO"),
                call(
                    "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"
                ),
                call(
                    "MT	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897"
                ),
            ]
        )
