from unittest import TestCase

from filter_vcf.util.cleanAD import clean_ad


class TestCleanAD(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(clean_ad(line), None)

    def test_clean_ad_1_dot(self):
        line = "chrX	154766321	rs2728532	G	A	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	1/.:1:0,900,8:425/483:0/0,425/483:0:INF:908"
        expected = "chrX	154766321	rs2728532	G	A	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	1/.:1:0,900:425/483:0/0,425/483:0:INF:908"

        self.assertEqual(clean_ad(line), expected)

    def test_clean_ad_dot_1(self):
        line = "chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,900,8:425/483:0/0,425/483:0:INF:908"
        expected = "chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,8:425/483:0/0,425/483:0:INF:908"

        self.assertEqual(clean_ad(line), expected)

    def test_clean_ad_two_values(self):
        line = "chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,900:425/483:0/0,425/483:0:INF:908"
        expected = "chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,900:425/483:0/0,425/483:0:INF:908"

        self.assertEqual(clean_ad(line), expected)

    def test_does_not_modify_non_multiallelic_line(self):
        line = "chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO	1/1:1.000:0,681:327/354:0/0,327/354:0"

        self.assertEqual(clean_ad(line), line)
