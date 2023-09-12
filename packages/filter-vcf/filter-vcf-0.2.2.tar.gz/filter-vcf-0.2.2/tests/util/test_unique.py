from unittest import TestCase

from filter_vcf.util.unique import keep_unique_line


class TestKeepUniqueLine(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(keep_unique_line(line, None), None)

    def test_returns_line_if_no_previous(self):
        line = "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"

        self.assertEqual(keep_unique_line(line, None), line)

    def test_returns_none_if_same_as_previous(self):
        line = "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"
        previous_line = line

        self.assertEqual(keep_unique_line(line, previous_line), None)

    def test_returns_line_if_not_same_as_previous(self):
        line = "1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"
        previous_line = "rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781"

        self.assertEqual(keep_unique_line(line, previous_line), line)
