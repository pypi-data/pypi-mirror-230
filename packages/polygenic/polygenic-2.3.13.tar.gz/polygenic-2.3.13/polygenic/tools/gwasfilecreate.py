from polygenic.data.gwas import Gwas
from calendar import c
import sys
import os

import polygenic.tools.utils as utils
import polygenic.data.csv_accessor as csv_accessor

def run(args):
    gwas = Gwas()
    gwas.load(args.input, vars(args))
    gwas.filter_by_pvalue()
    gwas.filter_by_complementary_alleles()
    gwas.filter_only_snps()
    gwas.annotate_with_gnomad()
    gwas.annotate_with_beta()
    gwas.convert_to_grch38()
    gwas.lasso_clump()
    gwas.annotate_with_gnomad(force=True)
    gwas.annotate_with_af()
    gwas.model()
    gwas.save(args.output)