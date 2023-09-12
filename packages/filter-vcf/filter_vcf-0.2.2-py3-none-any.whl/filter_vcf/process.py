import os
import shutil
from lifeomic_logging import scoped_logger
import tempfile


from filter_vcf.util.sortVcf import sort_vcf
from filter_vcf.util.normalize import normalize
from filter_vcf.util.decompose import decompose
from filter_vcf.util.filterContigs import filter_contigs
from filter_vcf.util.checkArgs import check_args
from filter_vcf.util.lineNormalization import perform_line_normalization


def normalize_vcf(arguments: dict):
    """
    Arguments:
        reference - path to reference genome
            GRCh37 or GRCh38

        input - Path to input vcf file(s) (.vcf/.tcf or .vcf.gz/.tcf.gz).

        output - path for output VCF (.vcf or .vcf.gz)

        decompose - default set to True
            Splits multiallelic variants.

        normalize - default set to True
            Parsimony and left alignment pertaining to the nature of a variant's length and position

        unique - default set to True
            Remove any duplicate variants from VCF

        filterContig - default set to False
            Filters out unsupported contigs from VCF

        depth - default set to True
            Calculate DP (depth) from summing the AD genotype field.

        filters - default set to "PASS"
            List of user specified FILTER labels to keep formatted as string with ":" delimiter. i.e. "PASS:sb"
    """

    with scoped_logger(__name__) as log:
        # Setup file paths and working variables
        args = check_args(arguments, log)

        with tempfile.TemporaryDirectory() as tmp_dir:
            os.makedirs(f"{tmp_dir}/ref/")

            ref_file = (
                f"{tmp_dir}/ref/GRCh37.fa.gz"
                if args["reference"].endswith("37.fa.gz")
                else f"{tmp_dir}/ref/GRCh38.fa.gz"
            )
            shutil.copyfile(f"{args['reference']}", ref_file)

            file_name = args["input"].split("/")[-1].replace(" ", "")
            in_file = f"{tmp_dir}/{file_name}"
            if not in_file.endswith(".gz"):
                in_file = in_file + ".gz"

            # Begin vcf processing
            vcf_in = args["input"]

            log.info("Performing initial sort and bgzip compression")
            sort_vcf(vcf_in, f"{tmp_dir}/sorted", in_file)

            if args["filterContig"]:
                log.info("Filtering contigs from VCF")
                filter_contigs(in_file, tmp_dir)

            if args["decompose"]:
                log.info("Decomposing VCF")
                decompose(in_file, tmp_dir)

            if args["normalize"]:
                log.info("Normalizing VCF")
                normalize(in_file, ref_file, tmp_dir, args["filterContig"], log)

            perform_line_normalization(in_file, tmp_dir, args)

            log.info("Performing final sort and bgzip compression")
            sort_vcf(in_file, f"{tmp_dir}/sorted", args["output"])

            return args
