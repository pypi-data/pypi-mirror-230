from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.filterContigs import filter_contigs, regions

logger = Mock()


class TestFilterContigs(TestCase):
    @patch("subprocess.run")
    @patch("os.rename")
    def test_filter_contigs(self, mock_rename, mock_subprocess):
        filter_contigs("in.vcf.gz", "tmp_dir", logger)

        mock_subprocess.assert_has_calls(
            [
                call("tabix -p vcf in.vcf.gz", shell=True, check=True),
                call(
                    f'bcftools view  -r "{regions}" in.vcf.gz -o tmp_dir/regions.vcf.gz -O z ',
                    shell=True,
                    check=True,
                ),
            ]
        )
        mock_rename.assert_called_once_with("tmp_dir/regions.vcf.gz", "in.vcf.gz")
