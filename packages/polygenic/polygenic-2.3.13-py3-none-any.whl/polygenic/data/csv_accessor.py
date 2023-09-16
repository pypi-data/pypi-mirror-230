"""
high level support for csv files
"""
import logging
import os
import sys
import numpy as np
from tqdm import tqdm

import pandas as pd
from polygenic.error.polygenic_exception import PolygenicException

logger = logging.getLogger('polygenic.data.' + __name__)

class CsvAccessor(object):
    """
    class for reading csv files
    """

    def __init__(self, csv_path: str, column_mappings: dict = None):
        super().__init__()
        self.__path = csv_path
        self.__delimiter = '\t'
        self.__column_name_mapping = {}
        if not os.path.exists(self.__path):
            raise PolygenicException(f"Can not access {self.__path}")
        self.__data = self.read_data()
        if column_mappings is not None:
            self.standardize_column_names(column_mappings)



    def __find_name_of_column_by_list_of_synonyms(self, names: list, equals_instead_of_contains: bool = True):
        for column_name in self.__data.columns:
            for name in names:
                if name is not None:
                    if equals_instead_of_contains:
                        if name.lower() == column_name.lower():
                            return column_name
                    else:
                        if name.lower() in column_name.lower():
                            return column_name
        return None

    def __map_column_names(self, column_names: dict):
        """
        map the column names to the internal names
        """
        self.__column_name_mapping.update({'rsid': self.__find_name_of_column_by_list_of_synonyms([column_names.get('rsid_column_name'), 'rsid', 'SNP'])})
        self.__column_name_mapping.update({'chromosome': self.__find_name_of_column_by_list_of_synonyms([column_names.get('chromosome_column_name'), 'chromosome', 'chrom', 'chr'])})
        self.__column_name_mapping.update({'gnomad': self.__find_name_of_column_by_list_of_synonyms([column_names.get('gnomadid_column_name'), 'gnomadid', 'gnomad'])})
        self.__column_name_mapping.update({'position': self.__find_name_of_column_by_list_of_synonyms([column_names.get('position_column_name'), 'position', 'pos', 'bp'])})
        self.__column_name_mapping.update({'ref': self.__find_name_of_column_by_list_of_synonyms([column_names.get('ref_allele_column_name'), 'ref', 'reference', 'ref_allele', 'A1'])})
        self.__column_name_mapping.update({'alt': self.__find_name_of_column_by_list_of_synonyms([column_names.get('alt_allele_column_name'), 'alt', 'alt_allele', 'other_allele', 'effect', 'effect_allele', 'A2'])})
        self.__column_name_mapping.update({'effect': self.__find_name_of_column_by_list_of_synonyms([column_names.get('effect_allele_column_name'), 'effect', 'effect_allele', 'alt', 'A2'])})
        self.__column_name_mapping.update({'pvalue': self.__find_name_of_column_by_list_of_synonyms([column_names.get('pvalue_column_name'), 'pvalue', 'p'])})
        self.__column_name_mapping.update({'beta': self.__find_name_of_column_by_list_of_synonyms([column_names.get('beta_column_name'), 'beta', 'beta_coefficient'])})
        self.__column_name_mapping.update({'or': self.__find_name_of_column_by_list_of_synonyms([column_names.get('af_column_name'), 'or'])})
        self.__column_name_mapping.update({'af': self.__find_name_of_column_by_list_of_synonyms([column_names.get('af_column_name'), 'af'])})
        self.__column_name_mapping.update({'info': self.__find_name_of_column_by_list_of_synonyms([column_names.get('info_column_name'), 'info'])})
        # if thers is no chromosome and position throw error
        if self.__column_name_mapping.get('chromosome') is None or self.__column_name_mapping.get('position') is None:
            raise PolygenicException("chromosome and position column names must be provided")


    def get_column_names(self):
        """
        return the column names
        """
        return self.__data.columns

    def standardize_column_names(self, column_names: dict):
        """
        standardize the column names
        """
        renaming_dict = {}

        self.__map_column_names(column_names)
        for key, value in self.__column_name_mapping.items():
            if value is not None:
                renaming_dict.update({value: key}) 
            
        self.__data.rename(columns=renaming_dict, inplace=True)
        ### if effect and reference are the same, then we should add additional reference column
        if self.__column_name_mapping.get("ref") == self.__column_name_mapping.get("effect"):
            if 'ref' not in self.__data.columns:
                self.__data['ref'] = self.__data['effect']
            if 'effect' not in self.__data.columns:
                self.__data['effect'] = self.__data['ref']
        ### the same for alt
        if self.__column_name_mapping.get("alt") == self.__column_name_mapping.get("effect"):
            if 'alt' not in self.__data.columns:
                self.__data['alt'] = self.__data['effect']
            if 'effect' not in self.__data.columns:
                self.__data['effect'] = self.__data['alt']

        ### if there are columns missing fill with None
        for key in column_names.keys():
            if key not in self.__data.columns:
                self.__data[key] = None
        self.__data = self.__data[column_names.keys()]


        

    def get_data(self):
        """
        return the dataframe
        """
        return self.__data

    def read_data(self):
        """
        read the csv file and return a dataframe
        """
        temp = pd.read_csv(filepath_or_buffer = self.__path, sep = self.__delimiter, nrows = 500)
        n = len(temp.to_csv(index=False))
        df = [temp[:0]]
        t = 500 * int(os.path.getsize(self.__path)/n*500*2.5/10**5) + 1
        with tqdm(total = t, file = sys.stdout, leave=False) as pbar:
            for i,chunk in enumerate(pd.read_csv(self.__path, sep = self.__delimiter, chunksize=10**5, low_memory=False)):
                df.append(chunk)
                pbar.set_description('Reading csv chunks (estimated): %d' % ((1 + i) * 500))
                pbar.update(500)

        # data = temp[:0].append(df)
        data = pd.concat([temp[:0]] + df)

        del df
        return data

    def get_symbol_for_genomic_position(self, chrom, pos):
        """
        return the symbol for a genomic position
        """
        data = self.__data
        data = data.loc[data["chromosome"] == str(chrom)]
        if len(data.index) == 0:
            return None
        data = data.assign(pos_start = abs(data["start"] - np.int64(pos)),
                           pos_end = abs(data["end"] - np.int64(pos)))
        data = data.assign(position = data[["pos_start", "pos_end"]].min(axis = 1))
        return data.sort_values(by=['pos_start'])['symbol'].head(1).iloc[0]
