from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.normalize import normalize

mock_log = Mock()


@patch("subprocess.run")
@patch("os.rename")
@patch("filter_vcf.util.normalize.detect_vcf")
class TestNormalize(TestCase):
    @patch("filter_vcf.util.normalize.convert_chr_name")
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_normalize_chr(
        self,
        mock_remove,
        mock_exists,
        mock_convert_chr_name,
        mock_detect_vcf,
        mock_rename,
        mock_subprocess,
    ):
        mock_detect_vcf.return_value = "chr"

        normalize("in.vcf.gz", "ref.fa.gz", "tmp_dir", False, mock_log)

        mock_detect_vcf.assert_called_once_with("in.vcf.gz")
        mock_exists.assert_called_once_with("in.vcf.gz.tbi")
        mock_remove.assert_called_once_with("in.vcf.gz.tbi")
        mock_convert_chr_name.assert_has_calls([call("in.vcf.gz", "num"), call("in.vcf.gz", "chr")])
        mock_subprocess.assert_has_calls(
            [
                call("tabix -p vcf in.vcf.gz", shell=True, check=True),
                call(
                    "vt normalize -n -r ref.fa.gz in.vcf.gz -o tmp_dir/normalized.vcf",
                    shell=True,
                    check=True,
                ),
                call("gzip tmp_dir/normalized.vcf", shell=True, check=True),
            ]
        )
        mock_rename.assert_called_once_with("tmp_dir/normalized.vcf.gz", "in.vcf.gz")

    def test_normalize_num(
        self,
        mock_detect_vcf,
        mock_rename,
        mock_subprocess,
    ):
        mock_detect_vcf.return_value = "num"

        normalize("in.vcf.gz", "ref.fa.gz", "tmp_dir", False, mock_log)

        mock_detect_vcf.assert_called_once_with("in.vcf.gz")
        mock_subprocess.assert_has_calls(
            [
                call("tabix -p vcf in.vcf.gz", shell=True, check=True),
                call(
                    "vt normalize -n -r ref.fa.gz in.vcf.gz -o tmp_dir/normalized.vcf",
                    shell=True,
                    check=True,
                ),
                call("gzip tmp_dir/normalized.vcf", shell=True, check=True),
            ]
        )
        mock_rename.assert_called_once_with("tmp_dir/normalized.vcf.gz", "in.vcf.gz")
