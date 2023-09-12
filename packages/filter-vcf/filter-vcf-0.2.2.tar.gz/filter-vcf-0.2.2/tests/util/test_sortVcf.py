from unittest import TestCase
from unittest.mock import patch, call, Mock

from filter_vcf.util.sortVcf import write_chunk, sort_vcf, get_sort_key
from tests.utils import FileMock


class TestGetSortKey(TestCase):
    def test_get_sort_key(self):
        result = get_sort_key(
            "chr1\t35910077\trs1293956811\tA\tG\t.\t.\tRS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827"
        )
        self.assertEqual(result, ("chr1", 35910077, "A", "G"))


class TestWriteChunk(TestCase):
    @patch("gzip.open")
    @patch("filter_vcf.util.sortVcf.natsorted")
    def test_write_chunk(
        self,
        mock_natsorted: Mock,
        mock_open: Mock,
    ):
        mock_natsorted.return_value = ["line1", "line2", "line3"]
        mock_writelines = Mock()
        mock_open.return_value.__enter__.return_value = FileMock(writelines_mock=mock_writelines)

        result = write_chunk(["line3", "line2", "line1"], 1, "working_dir")

        self.assertEqual(result, "working_dir/chunk_1.vcf.gz")
        mock_natsorted.assert_called_once_with(["line3", "line2", "line1"], key=get_sort_key)
        mock_open.assert_any_call("working_dir/chunk_1.vcf.gz", "wt")


mock_mkdir = Mock()


class TestSortVcf(TestCase):
    @patch("filter_vcf.util.sortVcf.write_chunk")
    @patch("filter_vcf.util.sortVcf.merge")
    @patch("filter_vcf.util.sortVcf.Path", return_value=Mock(mkdir=mock_mkdir))
    @patch("filter_vcf.util.sortVcf.natsort_keygen")
    @patch("subprocess.run")
    @patch("gzip.open")
    def test_sort_vcf(
        self,
        mock_open: Mock,
        mock_run: Mock,
        mock_natsort_keygen: Mock,
        mock_path: Mock,
        mock_merge: Mock,
        mock_write_chunk: Mock,
    ):
        mock_merge.return_value = ["line1", "line2", "line3"]
        chunk_files = [
            "working_dir/chunk_0.vcf.gz",
            "working_dir/chunk_1.vcf.gz",
        ]
        mock_write_chunk.side_effect = chunk_files
        mock_writelines = Mock()
        mock_open.return_value.__enter__.return_value = FileMock(
            ["#header", "line1", "line2", "line3"], writelines_mock=mock_writelines
        )

        sort_vcf("in.vcf.gz", "working_dir", "out.vcf.gz", chunk_size=2)

        mock_path.assert_called_once_with("working_dir")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_chunk.assert_has_calls(
            [
                call(["line1", "line2"], 0, "working_dir"),
                call(["line3"], 1, "working_dir"),
            ]
        )
        mock_natsort_keygen.assert_called_once_with(get_sort_key)
        self.assertEqual(mock_merge.call_args_list[0][1], {"key": mock_natsort_keygen.return_value})
        mock_open.assert_any_call("in.vcf.gz", "rt")
        mock_open.assert_any_call("working_dir/tmp_out.vcf.gz", "wt")
        mock_run.assert_called_once_with(
            "bcftools view -Oz -o out.vcf.gz working_dir/tmp_out.vcf.gz", shell=True, check=True
        )
        mock_writelines.assert_has_calls([call(["#header"]), call(["line1", "line2", "line3"])])
