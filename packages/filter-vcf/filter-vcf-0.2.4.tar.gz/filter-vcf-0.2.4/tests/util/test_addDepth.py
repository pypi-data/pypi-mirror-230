from unittest import TestCase

from filter_vcf.util.addDepth import add_depth_to_line


class TestAddDepthToLine(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(add_depth_to_line(line), None)

    def test_add_depth_to_line(self):
        line = "chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO	0/1:0.453:524,434:417/541:234/290,183/251:4"
        expected = "chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO:DP	0/1:0.453:524,434:417/541:234/290,183/251:4:958"
        self.assertEqual(add_depth_to_line(line), expected)

    def test_does_not_modify_line_that_already_has_depth(self):
        line = "chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO:DP	0/1:0.453:524,434:417/541:234/290,183/251:4:958"
        self.assertEqual(add_depth_to_line(line), line)
