import sys

import pandas as pd
import numpy as np
import logging
from tqdm import tqdm

from polygenic.data.csv_accessor import CsvAccessor
from polygenic.data.vcf_accessor import VcfAccessor
import polygenic.tools.utils as utils

logger = logging.getLogger('polygenic.data.' + __name__)
class Gwas(object):

    """
    class for manipulating gwas data
    """

    column_mappings = {

        'chromosome': {'synonyms': ['chromosome', 'chrom', 'chr'], 'obligatory': True, 'class': str},
        'position': {'synonyms': ['position', 'pos', 'bp'], 'obligatory': False, 'class': int},
        'rsid': {'synonyms': ['rsid', 'snp', 'id'], 'obligatory': False, 'class': str},
        'gnomad': {'synonyms': ['gnomadid', 'gnomad'], 'obligatory': False, 'class': str},
        'ref': {'synonyms': ['ref', 'reference', 'ref_allele', 'A1'], 'obligatory': False, 'class': str},
        'alt': {'synonyms': ['alt', 'alt_allele', 'other_allele', 'effect', 'effect_allele', 'A2'], 'obligatory': False, 'class': str},
        'effect': {'synonyms': ['effect', 'effect_allele', 'alt', 'A2'], 'obligatory': False, 'class': str},
        'pvalue': {'synonyms': ['pvalue', 'p'], 'obligatory': False, 'class': float},
        'beta': {'synonyms': ['beta', 'beta_coefficient'], 'obligatory': False, 'class': float},
        'or': {'synonyms': ['or'], 'obligatory': False, 'class': float},
        'af': {'synonyms': ['af'], 'obligatory': False, 'class': float},
        'info': {'synonyms': ['info'], 'obligatory': False, 'class': float}

    }


    def __init__(self):
        self.data = pd.DataFrame(columns=self.column_mappings.keys())
        self.iter_idx = 0

    def __get_size(self):
        return self.data.shape[0]
    
    def __iter__(self):
        self.iter_idx = 0
        return self

    def __next__(self):
        self.iter_idx += 1
        if self.iter_idx > self.__get_size():
            raise StopIteration
        return self.data.iloc[self.iter_idx]        

    def __append(self, gwas_record):
        self.data = pd.concat([self.data, pd.DataFrame(gwas_record, index=[0])], ignore_index=True, sort=False)

    def load(self, input_path: str, column_mappings: dict = {}):
        logging.debug("Loading csv file: %s", input_path)

        """
        Load GWAS data from a file
        """
        self.data = CsvAccessor(input_path, column_mappings=self.column_mappings).get_data()

    def save(self, output_path: str):
        self.data.to_csv(output_path, index=False, sep='\t')

    def filter_by_pvalue(self, pvalue_threshold: float = 0.0001):
        """
        filter gwas data
        """
        ### filtering rows based on p value, convert p value to float before comparison
        self.data = self.data[self.data['pvalue'].astype(float) < pvalue_threshold]

    def filter_by_complementary_alleles(self):
        """
        remove complementary alleles
        where ref and alt are either G and C or A and T
        """
        self.data = self.data[~((self.data['ref'] == 'G') & (self.data['alt'] == 'C'))]
        self.data = self.data[~((self.data['ref'] == 'C') & (self.data['alt'] == 'G'))]
        self.data = self.data[~((self.data['ref'] == 'A') & (self.data['alt'] == 'T'))]
        self.data = self.data[~((self.data['ref'] == 'T') & (self.data['alt'] == 'A'))]

    def filter_only_snps(self):
        """
        remove indels
        """
        self.data = self.data[self.data['ref'].str.len() == 1]
        self.data = self.data[self.data['alt'].str.len() == 1]

    def annotate_with_gnomad(self, force: bool = False):
        """
        annotate with gnomad
        """
        ### if gnomad id column is empty add gnomad id records in ofrmt chromosome-position-ref-alt
        if self.data['gnomad'].isnull().values.any() or force:
            self.data['gnomad'] = self.data.apply(lambda row: '-'.join((str(row['chromosome']), str(row['position']), row['ref'], row['alt'])), axis=1)

    def annotate_with_beta(self):
        """
        annotate with beta
        """
        ### if beta column is empty add beta records in format log(OR)
        if self.data['beta'].isnull().values.any():
            self.data['beta'] = self.data.apply(lambda row: np.log(row['or']), axis=1)

    def complementary(nucleotide: str, second_nucleotide: str = None):
        if second_nucleotide is not None:
            return 'N'
        if nucleotide == 'G':
            return 'C'
        elif nucleotide == 'C':
            return 'G'
        elif nucleotide == 'A':
            return 'T'
        elif nucleotide == 'T':
            return 'A'
        else:
            return None
        


    def convert_to_grch38(self):
        grch38_ref_vcf = VcfAccessor('/home/marpiech/data/vcf/dbsnp155.grch38.norm.vcf.gz')
        ### for each item in data as dictionary
        for idx, row in tqdm(self.data.iterrows(), total=self.data.shape[0]):
            ### continue if multiple alts or refs
            if len(row['alt']) > 1 or len(row['ref']) > 1:
                self.data.drop(idx, inplace=True)
                continue
            ### for rsid from row get record from vcf   
            record = grch38_ref_vcf.get_record_by_rsid(row['rsid'])
            if record is not None:
                if row['ref'] == record.get_ref() and row['alt'] in record.get_alt():
                    self.data.at[idx, 'chromosome'] = record.get_chrom()
                    self.data.at[idx, 'position'] = record.get_pos()
                    self.data.at[idx, 'effect'] = self.data.at[idx, 'alt']
                elif row['ref'] in record.get_alt() and row['alt'] == record.get_ref():
                    self.data.at[idx, 'chromosome'] = record.get_chrom()
                    self.data.at[idx, 'position'] = record.get_pos()
                    self.data.at[idx, 'ref'] = row['alt']
                    self.data.at[idx, 'alt'] = row['ref']
                    self.data.at[idx, 'beta'] = -row['beta']
                    self.data.at[idx, 'effect'] = self.data.at[idx, 'alt']
                    # if self.data.at[idx, 'effect'] == row['alt']:
                    #     self.data.at[idx, 'effect'] = row['ref']
                    # elif self.data.at[idx, 'effect'] == row['ref']:
                    #     self.data.at[idx, 'effect'] = row['alt']
                elif self.complementary(row['ref']) == record.get_ref() and self.complementary(row['alt']) in record.get_alt():
                    self.data.at[idx, 'chromosome'] = record.get_chrom()
                    self.data.at[idx, 'position'] = record.get_pos()
                    self.data.at[idx, 'ref'] = self.complementary(row['ref'])
                    self.data.at[idx, 'alt'] = self.complementary(row['alt'])
                    self.data.at[idx, 'effect'] = self.data.at[idx, 'alt']
                    # self.data.at[idx, 'effect'] = self.complementary(row['effect'])
                elif self.complementary(row['ref']) in record.get_alt() and self.complementary(row['alt']) == record.get_ref():
                    self.data.at[idx, 'chromosome'] = record.get_chrom()
                    self.data.at[idx, 'position'] = record.get_pos()
                    self.data.at[idx, 'ref'] = self.complementary(row['alt'])
                    self.data.at[idx, 'alt'] = self.complementary(row['ref'])
                    self.data.at[idx, 'effect'] = self.data.at[idx, 'alt']
                    # self.data.at[idx, 'effect'] = self.complementary(row['effect'])
                    # if self.data.at[idx, 'effect'] == row['alt']:
                    #     self.data.at[idx, 'effect'] = row['ref']
                    # elif self.data.at[idx, 'effect'] == row['ref']:
                    #     self.data.at[idx, 'effect'] = row['alt']
                    self.data.at[idx, 'beta'] = -row['beta']
                else:
                    ### remove row if not found in vcf
                    self.data.drop(idx, inplace=True)
            else:
                ### remove row if not found in vcf
                self.data.drop(idx, inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    ### lasso helper function
    def is_in_the_same_window(self, first_snp, second_snp, window_size):
        return first_snp['chromosome'] == second_snp['chromosome'] and \
            abs(int(first_snp['position']) - int(second_snp['position'])) <= window_size

    ### lasso helper function
    def flatten(self, lst):
        return sum(lst, [])

    ### lasso helper function
    def local_minima(self, lst):
        if len(lst) < 2:
            return list(range(len(lst)))
        
        lmin = True
        curr = list()
        local_minima = list()
        
        for i, x in enumerate(lst[:-1]):
            if lst[i + 1] == x and lmin:
                curr.append(i)
            if lst[i + 1] < x:
                lmin = True
                curr = list()
            if lst[i + 1] > x:
                if lmin:
                    local_minima.append(curr + [i])
                lmin = False

        if lst[-1] < lst[-2] or (lmin and lst[-1] == lst[-2]):
            local_minima.append(curr + [len(lst) - 1])
        
        return self.flatten(local_minima)

    ### lasso helper function
    def invert(self, a):
        return [-x for x in a]

    ### lasso helper function
    def local_maxima(self, a):
        return self.local_minima(self.invert(a))

    def lasso_clump(self):
        clump_p = 0.00000001
        clump_kb = 100
        clump_field = 'pvalue'
        clump_snp_field = 'rsid'

        # cluster snps into regions
        region = []
        new_data = pd.DataFrame(columns=self.column_mappings.keys())
        for index, row in tqdm(self.data.iterrows(), total=self.data.shape[0]):
            if float(row[clump_field]) > float(clump_p):
                continue
            if not region:
                region.append(row)
                continue
            if self.is_in_the_same_window(region[-1], row, window_size = int(clump_kb) * 1000):
                region.append(row)
                continue
            pvalues = [float(x[clump_field]) for x in region]
            min_index = pvalues.index(min(pvalues))
            new_data = pd.concat([new_data, pd.DataFrame([region[min_index]], columns=self.column_mappings.keys())], ignore_index=True)
            region = [row]
        if region:
            pvalues = [float(x[clump_field]) for x in region]
            min_index = pvalues.index(min(pvalues))
            new_data = pd.concat([new_data, pd.DataFrame([region[min_index]], columns=self.column_mappings.keys())], ignore_index=True)
        self.data = new_data

    def annotate_with_af(self):
        af_vcf = VcfAccessor('/home/marpiech/data/vcf/gnomad.3.1.vcf.gz')
        ### if af is null fill it based on vcf info field
        if self.data['af'].isnull().values.any():
            for idx, row in tqdm(self.data.iterrows(), total=self.data.shape[0]):
                if row['af'] is None:
                    print("getting record from af vcf")
                    record = af_vcf.get_record_by_gnomadid(row['gnomad'])
                    print("record found")
                    if record is not None:
                        self.data.at[idx, 'af'] = float(record.get_info_field('AF_nfe'))
                    else:
                        self.data.at[idx, 'af'] = 0
        #self.data = utils.annotate_with_af(self.data, af_vcf, af_field = "AF_eur", default_af = 0)

    def model(self):
        """
        model gwas data
        """
        logger.info("Annotating with symbols")
        #data = utils.annotate_with_symbols(data, args.gene_positions)
        #genes = utils.get_gene_symbols(data)
        description = {}
        #description["arguments"] = utils.args_to_dict(args)
        description["parameters"] = utils.simulate_parameters(self.data)
        description["pmid"] = ["25826379"]
        #description["genes"] = genes
    
        utils.write_model(self.data, description, "/tmp/polygenic/test/model.yml", included_fields_list = ['ref', 'gnomad', 'af'])



                

        

    # if not "ref" in validated_line:
    #     validated_line['ref'] = record.get_ref()
    # if not (validated_line['ref'] == record.get_ref() and validated_line['alt'] in record.get_alt()): 
    #     message = "REF mismatch. Line: " + validated_line['ref'] + "/" + validated_line['alt'] + " . Reference: " + record.get_ref() + "/" + str(record.get_alt()) + "."
    #     if validated_line['ref'] == invert_nucleotides(validated_line['alt']):
    #         if verbose: error_print("ERROR: " + message + " REF and ALT are complementary. Not sure whether to swap (beta will be negative) or invert (beta will be unchanged) nucleotides.")
    #         validated_line["status"] = "ERROR"
    #         return None if strict else validated_line
    #     if (invert_nucleotides(validated_line['ref']) == record.get_ref() and invert_nucleotides(validated_line['alt']) in record.get_alt()):
    #         validated_line['ref'] = invert_nucleotides(validated_line['ref'])
    #         validated_line['alt'] = invert_nucleotides(validated_line['alt'])
    #         if verbose: error_print("WARNING: " + message + " REF and ALT are on '-' strand notation. Succesfull inversion.")
    #         validated_line["status"] = "WARNING. Minus strand notation"
    #         if "pos" not in validated_line: validated_line["pos"] = record.get_pos()
    #         if validated_line["pos"] == "": validated_line["pos"] = record.get_pos()
    #         validated_line["gnomadid"] = record.get_chrom().replace("chr", "") + ":" + record.get_pos() + "_" + record.get_ref() + "_" + validated_line['alt']
    #         return validated_line if ignore_warnings else None
    #     if (validated_line['ref'] in record.get_alt() and validated_line['alt'] == record.get_ref()):
    #         ref = validated_line['ref']
    #         alt = validated_line['alt']
    #         validated_line['ref'] = alt
    #         validated_line['alt'] = ref
    #         if invert_field is not None:
    #             validated_line[invert_field] = - float(validated_line[invert_field])
    #         if verbose: error_print("WARNING: " + message + " REF and ALT are swapped. Succesful swap.")
    #         validated_line["status"] = "WARNING. Inverted ref with alt"
    #         if "pos" not in validated_line: validated_line["pos"] = record.get_pos()
    #         if validated_line["pos"] == "": validated_line["pos"] = record.get_pos()
    #         validated_line["gnomadid"] = record.get_chrom().replace("chr", "") + ":" + record.get_pos() + "_" + record.get_ref() + "_" + validated_line['alt']
    #         return validated_line if ignore_warnings else None
    #     if (invert_nucleotides(validated_line['ref']) in record.get_alt() and invert_nucleotides(validated_line['alt']) == record.get_ref()):
    #         ref = invert_nucleotides(validated_line['ref'])
    #         alt = invert_nucleotides(validated_line['alt'])
    #         validated_line['ref'] = alt
    #         validated_line['alt'] = ref
    #         if invert_field is not None:
    #             validated_line[invert_field] = - float(validated_line[invert_field])
    #         if verbose: error_print("WARNING: " + message + " REF and ALT are on '-' strand notation and swapped. Succesfull swap and inversion.")
    #         validated_line["status"] = "WARNING. Inverted ref with alt"
    #         if "pos" not in validated_line: validated_line["pos"] = record.get_pos()
    #         if validated_line["pos"] == "": validated_line["pos"] = record.get_pos()
    #         validated_line["gnomadid"] = record.get_chrom().replace("chr", "") + ":" + record.get_pos() + "_" + record.get_ref() + "_" + validated_line['alt']
    #         return validated_line if ignore_warnings else None
    #     if verbose: error_print("ERROR: " + message + ". REF and ALT do not match.")
    #     validated_line["status"] = "ERROR"
    #     return None if strict else validated_line
    # if record.get_id():
    #     validated_line["rsid"] = record.get_id()
    # if "pos" not in validated_line: validated_line["pos"] = record.get_pos()
    # if validated_line["pos"] == "": validated_line["pos"] = record.get_pos()
    # validated_line["gnomadid"] = record.get_chrom().replace("chr", "") + ":" + record.get_pos() + "_" + record.get_ref() + "_" + validated_line['alt']
    # validated_line["status"] = "SUCCESS"
    # return validated_line

        

# """
# high level support for gwas files
# """
# import logging
# import sys
# import math
# import csv as csvlib

# from tqdm import tqdm

# import pandas as pd
# import numpy as np
# from scipy.signal import argrelextrema

# from plotnine import ggplot
# from plotnine import geom_point, geom_hline
# from plotnine import aes, theme, theme_void, theme_minimal, scale_fill_manual, scale_color_manual, scale_size_continuous
# from plotnine import element_rect, element_line
# from plotnine import *

# from polygenic.data.csv_accessor import CsvAccessor
# from polygenic.tools.data.chromsizes import Chromsizes
# from polygenic.tools.data.colors import Colors as colors
# from polygenic.error.polygenic_exception import PolygenicException

# logger = logging.getLogger('polygenic.data.' + __name__)

# class Gwas(object):

#     """
#     class for manipulating gwas data
#     """

#     COLUMN_NAMES = ['chromosome',
#                     'position',
#                     'gnomadid',
#                     'rsid',
#                     'ref',
#                     'alt',
#                     'effect',
#                     'pvalue',
#                     'beta',
#                     'or',
#                     'af']

#     def __init__(self):
#         super().__init__()
#         self.__data = {}
#         self.__size = 0
#         self.__iteridx = 0
#         self.__iterlist = 0

#     def __get_size(self):
#         if self.__size > 0:
#             return self.__size
#         for(positions) in self.__data.values():
#             self.__size += len(positions)
#         return self.__size

#     def __as_list(self):
#         data = []
#         for chromosome, positions in self.__data.items():
#             for position, values in positions.items():
#                 data.append(values)
#         return data

#     def __iter__(self):
#         self.__iteridx = 0
#         self.__iterlist = self.__as_list()
#         return self.__iterlist[self.__iteridx]

#     def __next__(self):
#         self.__iteridx += 1
#         if self.__iteridx > self.__get_size():
#             raise StopIteration
#         return self.__iterlist[self.__iteridx]

#     def __get_column_from_csv(self, csv, column_name):
#         if column_name in csv.get_column_names():
#             return csv.get_data()[column_name]
#         else:
#             # return vector filled with NaNs
#             return np.full(csv.get_data().shape[0], np.nan)

#     def filter(self, pvalue_threshold: float = 0.5):
#         """
#         filter gwas data
#         """
#         print("FILTER")
#         filtered_data = []
        
#         with tqdm(total = self.__get_size(), file = sys.stdout, leave=False) as pbar:
#             for chromosome, positions in self.__data.items():
#                 for position, gwas_record in positions.items():
#                     if gwas_record.get("pvalue") < pvalue_threshold:
#                         filtered_data.append(gwas_record)
#             pbar.set_description('Filtering records')
#             pbar.update(1)            
#         self.__data = filtered_data

#     def load(self, input_path: str, column_mappings: dict = {}):
#         logging.debug("Reading csv file: %s", input_path)
#         csv = CsvAccessor(input_path)
#         logging.debug("Standardizing column names")
#         csv.standardize_column_names(column_mappings)
#         logging.debug("Organizing data")

#         # organizing is implemented by array iteration in numpy for efficiency
#         with tqdm(total = csv.get_data().shape[0], file = sys.stdout, leave=True) as pbar:
#             chromosome_vector = self.__get_column_from_csv(csv, 'chromosome')
#             position_vector = self.__get_column_from_csv(csv, 'position')
#             rsid_vector = self.__get_column_from_csv(csv, 'rsid')
#             ref_vector = self.__get_column_from_csv(csv, 'ref')
#             alt_vector = self.__get_column_from_csv(csv, 'alt')
#             effect_vector = self.__get_column_from_csv(csv, 'effect')
#             pvalue_vector = self.__get_column_from_csv(csv, 'pvalue')
#             beta_vector = self.__get_column_from_csv(csv, 'beta')
#             or_vector = self.__get_column_from_csv(csv, 'or')
#             af_vector = self.__get_column_from_csv(csv, 'af')
            
#             chromosomes = list(np.unique(chromosome_vector))
#             for chromosome in chromosomes:
#                 if chromosome not in self.__data:
#                     self.__data.update({chromosome: {}})
#             for index in list(range(csv.get_data().shape[0])):
#                 values = {'chromosome': chromosome_vector[index],
#                             'position': position_vector[index],
#                             'gnomadid': "-".join((str(chromosome_vector[index]), str(position_vector[index]), str(ref_vector[index]), str(alt_vector[index]))),
#                             'rsid': rsid_vector[index],
#                             'ref': ref_vector[index],
#                             'alt': alt_vector[index],
#                             'effect': effect_vector[index],
#                             'pvalue': pvalue_vector[index],
#                             'beta': beta_vector[index],
#                             'or': or_vector[index],
#                             'af': af_vector[index]}
#                 self.__data[chromosome_vector[index]].update({int(position_vector[index]): values})
#                 pbar.set_description('Organizing records')
#                 pbar.update(1)
#             for chromosome, positions in self.__data.items():
#                 self.__data[chromosome] = dict(sorted(positions.items()))
    
#     def save(self, output_path: str):
#         logging.debug("Writing csv file: %s", output_path)
#         with open(output_path, 'w', encoding = 'UTF8') as file:
#             writer = csvlib.writer(file, delimiter = '\t', quotechar = '"', quoting = csvlib.QUOTE_NONE)
#             writer.writerow(self.COLUMN_NAMES)
#             for positions in self.__data.values():
#                 for position in positions.values():
#                     writer.writerow(position.values())

#     def __get_size(self):
#         size = 0
#         for(positions) in self.__data.values():
#             size += len(positions)
#         return size

#     # def clump(self):
#     #     if self.__clumped_data:
#     #         return self.__clumped_data
#     #     clumped_data = []
#     #     print(self.__get_size())
#     #     with tqdm(total = self.__get_size(), file = sys.stdout, leave=False) as pbar:
#     #         for chromosome, positions in self.__data.items():
#     #             p_sequence = np.array([])
#     #             pos_sequence = np.array([])
#     #             for position in positions.values():
#     #                 pbar.set_description('Clumping records')
#     #                 pbar.update(1)
#     #                 p_sequence = np.append(p_sequence, -math.log(position.get("pvalue"),10))
#     #                 pos_sequence = np.append(pos_sequence, position.get("position"))
#     #             extrema = argrelextrema(p_sequence, np.greater_equal, order=int(len(positions) / 10))[0]
#     #             for extremum in extrema:
#     #                 if p_sequence[extremum] > 5:
#     #                     clumped_data.append(positions[int(pos_sequence[extremum])])
#     #     self.__clumped_data = clumped_data
#     #     return clumped_data

#     # def validate(self):
#     #     """
#     #     validate gwas data
#     #     """
#     #     grch37_ref_vcf = 'polygenic/tests/resources/largefiles/dbsnp155.grch37.norm.vcf.gz'
#     #     grch38_ref_vcf = 'polygenic/tests/resources/largefiles/dbsnp155.grch38.norm.vcf.gz'
        

#     def __get_filtered_data(self, pvalue_threshold: float = 0.05):
#         """
#         return a filtered gwas data
#         """
#         filtered_data = []
        
#         with tqdm(total = self.__get_size(), file = sys.stdout, leave=False) as pbar:
#             for chromosome, positions in self.__data.items():
#                 for position, gwas_record in positions.items():
#                     if gwas_record.get("pvalue") < pvalue_threshold:
#                         filtered_data.append(gwas_record)
#             pbar.set_description('Filtering records')
#             pbar.update(1)            
#         return filtered_data

#     # def __get_filtered_data_for_manhattan_plot(self, evry_nth: int = 2, pvalue_threshold: float = 0.05):
#     #     """
#     #     return a filtered gwas data for manhattan plot
#     #     """
#     #     filtered_data = []
        
#     #     with tqdm(total = self.__get_size(), file = sys.stdout, leave=False) as pbar:
#     #         for chromosome, positions in self.__data.items():
#     #             for position, record in positions.items():
#     #                 if record.get("pvalue") < pvalue_threshold and int(position) % evry_nth == 0:
#     #                     filtered_data.append(record)
#     #         pbar.set_description('Filtering records')
#     #         pbar.update(1)
        
#     #     return filtered_data

#     # def plot_manhattan(self):
#     #     """
#     #     plot manhattan plot
#     #     """

#     #     threshold = 5
        
#     #     data = self.__get_filtered_data_for_manhattan_plot()
#     #     clumped_data = self.clump()
#     #     data_length = len(data)
#     #     clumped_data_length = len(clumped_data)
#     #     #data.append(clumped_data)
#     #     data = pd.DataFrame(data)
#     #     data['set'] = 'regular'
#     #     clumped_data = pd.DataFrame(clumped_data)
#     #     clumped_data['set'] = 'selected'
#     #     data = pd.concat([data, clumped_data], ignore_index=True, sort=False)
#     #     chromsizes = Chromsizes().chromsizes["GRCh37"]
#     #     cumulative_chromsizes = Chromsizes().chromsizes["GRCh37" + "_cumulative"]
#     #     # get summary length of all chromosomes
#     #     summary_length = sum(chromsizes.values())
#     #     print(data.shape)
#     #     print(str(data.iloc[0:3]))
#     #     print(clumped_data.shape)
#     #     print(str(clumped_data.iloc[0:3]))
#     #     min_beta = min(abs(clumped_data['beta']))
#     #     max_beta = max(abs(clumped_data['beta']))
#     #     # add cumulative position column to data
#     #     data['cumulative_position'] = data.apply(lambda row: int(row["position"]) + cumulative_chromsizes[str(int(row["chromosome"]))], axis=1)
#     #     # # add log10 pvalue column to data
#     #     data['log10_pvalue'] = data.apply(lambda row: -math.log10(row["pvalue"]), axis=1)
#     #     # add different color to every second chromosome
#     #     data['color'] = data.apply(lambda row: '0' if row["chromosome"] in ['X', 'Y'] or int(row["chromosome"]) % 2 == 1 else '1', axis=1)
#     #     # data['color'] = data.apply(lambda row: row['color'] if row['log10_pvalue'] < 8 else '2', axis=1)
#     #     # data['color'] = data.apply(lambda row: row['color'] if row['log10_pvalue'] < 20 else '3', axis=1)
#     #     data['color'] = data.apply(lambda row: row['color'] if row['set'] != 'selected' else '5', axis=1)
#     #     min_beta_size = 0.1
#     #     max_beta_size = 5
#     #     diff_beta_size = max_beta_size - min_beta_size
#     #     data['size'] = min_beta_size
#     #     data['size'] = data.apply(lambda row: row['size'] if row['set'] != 'selected' else (min_beta + diff_beta_size * ((abs(row['beta']) - min_beta) / max_beta)), axis=1)
    
    
#     #     color_dict = {'0': colors.grey, 
#     #                 '1': colors.grey_dark, 
#     #                 '2': colors.teal, 
#     #                 '3': colors.teal_dark, 
#     #                 '4': colors.teal_darker,
#     #                 '5': colors.pumpkin_light}

#     #     plot = (
#     #         ggplot(data, aes('cumulative_position', 'log10_pvalue', color = 'color', size = 'size')) + 
#     #         geom_point() +
#     #         geom_hline(yintercept = 8, color = colors.grey, size = 0.5, linetype = 'dashed') +
#     #         geom_hline(yintercept = 5, color = colors.pumpkin, size = 0.5, linetype = 'dashed') +
#     #         scale_color_manual(values=color_dict) +
#     #         scale_size_continuous(range=(min_beta_size,max_beta_size)) + 
#     #         theme(
#     #             legend_position = "none",
#     #             line = element_line(color = colors.grey, size = 1),
#     #             rect = element_rect(fill = colors.grey_lighter),
#     #             panel_grid_major = element_blank(),
#     #             panel_grid_minor = element_blank(),
#     #             panel_border = element_blank(),
#     #             panel_background = element_blank(),
#     #             axis_line = element_blank(),
#     #             axis_title_x = element_blank(),
#     #             axis_title_y = element_blank(),
#     #             axis_text_x = element_blank(),
#     #             axis_text_y = element_blank(),
#     #             axis_ticks = element_line(size = 1),
#     #             axis_ticks_length = 5,
#     #             axis_ticks_length_minor = 2,
#     #             axis_ticks_major_x = element_blank(),
#     #             axis_ticks_major_y = element_line(color = colors.grey_light),
#     #             axis_ticks_minor_y = element_line(color = colors.grey_light),
#     #         )
#     #     )

#     #     plot.save("/tmp/plot.png", height=6, width=8)



