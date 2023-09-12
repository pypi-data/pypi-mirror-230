from unittest import TestCase

from filter_vcf.util.userFilter import filter_line


class TestFilterLine(TestCase):
    def test_skips_nonexistent_line(self):
        line = None
        self.assertEqual(filter_line(line, "PASS"), None)

    def test_returns_line_for_exact_match(self):
        line = "11	42641414	rs1006891614	C	T	.	PASS;sb"
        filters = "PASS:sb"

        self.assertEqual(filter_line(line, filters), line)

    def test_discards_line_if_non_match_and_more_than_one_filter(self):
        line = "11	42641414	rs1006891614	C	T	.	PASS;sb;lowQ"
        filters = "PASS:sb"

        self.assertEqual(filter_line(line, filters), None)

    def test_returns_line_if_non_match_but_one_matching_filter(self):
        line = "11	42641414	rs1006891614	C	T	.	PASS"
        filters = "PASS:sb"

        self.assertEqual(filter_line(line, filters), line)

    def test_returns_none_for_non_match(self):
        line = "11	42641414	rs1006891614	C	T	.	PASS"
        filters = "sb"

        self.assertEqual(filter_line(line, filters), None)
