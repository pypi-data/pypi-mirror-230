from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.process import normalize_vcf

args = {
    "reference": "/path/to/GRCh37.fa.gz",
    "input": "/path/to/input.vcf",
    "output": "/path/to/output.vcf.gz",
    "normalize": True,
    "filterContig": True,
    "decompose": True,
    "unique": True,
    "depth": True,
    "filters": "PASS",
}

logger = Mock()


class TestNormalizeVCF(TestCase):
    @patch("filter_vcf.process.scoped_logger")
    @patch("tempfile.TemporaryDirectory")
    @patch("os.makedirs")
    @patch("filter_vcf.process.check_args", return_value=args)
    @patch("filter_vcf.process.sort_vcf")
    @patch("filter_vcf.process.filter_contigs")
    @patch("filter_vcf.process.decompose")
    @patch("filter_vcf.process.normalize")
    @patch("filter_vcf.process.perform_line_normalization")
    @patch("shutil.copyfile")
    def test_normalize_vcf(
        self,
        mock_copyfile: Mock,
        mock_perform_line_normalization: Mock,
        mock_normalize: Mock,
        mock_decompose: Mock,
        mock_filter_contigs: Mock,
        mock_sort_vcf: Mock,
        mock_check_args: Mock,
        mock_makedirs: Mock,
        mock_tempdir: Mock,
        mock_scoped_logger: Mock,
    ):
        mock_tempdir.return_value.__enter__.return_value = "/tmp"
        mock_scoped_logger.return_value.__enter__.return_value = logger

        normalize_vcf(args)

        mock_tempdir.assert_called_once()
        mock_makedirs.assert_called_once_with("/tmp/ref/")
        mock_copyfile.assert_called_once_with("/path/to/GRCh37.fa.gz", "/tmp/ref/GRCh37.fa.gz")
        mock_check_args.assert_called_once_with(args, logger)
        mock_sort_vcf.assert_has_calls(
            [
                call("/path/to/input.vcf", "/tmp/sorted", "/tmp/input.vcf.gz"),
                call("/tmp/input.vcf.gz", "/tmp/sorted", "/path/to/output.vcf.gz"),
            ]
        )
        mock_filter_contigs.assert_called_once_with("/tmp/input.vcf.gz", "/tmp")
        mock_decompose.assert_called_once_with("/tmp/input.vcf.gz", "/tmp")
        mock_normalize.assert_called_once_with(
            "/tmp/input.vcf.gz", "/tmp/ref/GRCh37.fa.gz", "/tmp", True, logger
        )
        mock_perform_line_normalization.assert_called_once_with("/tmp/input.vcf.gz", "/tmp", args)
