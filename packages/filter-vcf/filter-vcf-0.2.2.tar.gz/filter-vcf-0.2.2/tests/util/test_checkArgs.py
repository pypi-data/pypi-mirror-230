import logging
import os
from unittest import TestCase, mock

from filter_vcf.util.checkArgs import check_args

mock_log = mock.Mock()

BASE_PATH = os.path.abspath(os.path.dirname(__file__)).replace("/util", "")


class checkArgsErrors(TestCase):
    def test_check_args_errors(self):
        with self.assertRaises(TypeError) as cm:
            arguments = [
                {
                    "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                    "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                    "output": "",
                    "decompose": True,
                    "normalize": True,
                    "unique": True,
                    "filterContig": True,
                    "depth": True,
                    "filters": "PASS:sb",
                }
            ]

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Arguments must be input as dictionary. str was provided." in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "INCORRECT": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Unapproved input arguments detected. Please correct issues with the following arguments {{'INCORRECT', 'decompose'}}"
                in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh99.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Genome reference .fa.gz must be GRCh38 or GRCh37. Given: {arguments['reference']}"
                in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh38.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Genome reference .fa.gz file not found: {arguments['reference']}"
                in str(cm.exception)
            )

    def test_suffixes(self):
        arguments = {
            "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
            "input": f"{BASE_PATH}/resources/foundationSample.vcf",
            "output": "",
            "decompose": True,
            "normalize": True,
            "unique": True,
            "filterContig": True,
            "depth": True,
            "filters": "PASS:sb",
        }

        result = check_args(arguments, mock_log)

        self.assertEqual(
            result["output"], f"{BASE_PATH}/resources/foundationSample.nrm.filtered.vcf.gz"
        )

    def test_check_args_logs(self):
        test_log = logging.getLogger()

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": False,
                "normalize": False,
                "unique": False,
                "filterContig": False,
                "depth": False,
                "filters": "",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                f"WARN:root:No operations selected",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": True,
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                "Approved filter string not provided. Filter will be disabled and no variants will be filtered.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": "Yes",
                "normalize": "Yes",
                "unique": "Yes",
                "filterContig": "Yes",
                "depth": "Yes",
                "filters": "PASS:sb",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                "Approved boolean value not provided for argument: decompose. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[2],
                "Approved boolean value not provided for argument: normalize. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[3],
                "Approved boolean value not provided for argument: unique. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[4],
                "Approved boolean value not provided for argument: filterContig. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[5],
                "Approved boolean value not provided for argument: depth. Updating to 'True'.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "testOutput",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                f"Specified output file must end in .vcf or .vcf.gz. Given: testOutput \
             Setting output to .vcf.gz format.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": "Yes",
                "filters": "",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[0],
                f'Input arguments approved. Checked arguments: {{ "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz", "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz", "output": "", "decompose": True, "normalize": True, "unique": True, "filterContig": True, "depth": "Yes", "filters": "PASS:sb"}}',
            )
            self.assertTrue(
                cm.output[2],
                f'Input arguments approved. Checked arguments: {{ "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz", "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz", "output": f"{BASE_PATH}/resources/foundationSample.nrm.vcf.gz", "decompose": True, "normalize": True, "unique": True, "filterContig": True, "depth": True, "filters": "PASS:sb"}}',
            )
