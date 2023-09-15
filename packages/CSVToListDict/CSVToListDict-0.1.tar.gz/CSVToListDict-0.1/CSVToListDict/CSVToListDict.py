import csv
from logging import Logger
from os.path import isfile
from typing import List


class _FieldnamesMismatch(Exception):
    ...


class _FieldnamesAutoReadError(Exception):
    ...


class CSVToListDict:
    def __init__(self, csv_filepath, logger: Logger = None, fieldnames: list = None):
        self.list_dict = []

        if logger:
            self._logger = logger
        else:
            self._logger = Logger("dummy")

        if isfile(csv_filepath):
            self.csv_filepath = csv_filepath
        else:
            try:
                raise FileNotFoundError("The given CSV file cannot be found.")
            except FileNotFoundError as e:
                self._logger.error(e, exc_info=True)
                raise e

        if fieldnames:
            self._fieldnames = fieldnames
            self._logger.info("fieldnames were passed in as an attribute.")
        else:
            self._fieldnames = self._ReadCSVFieldnames()

    def _ReadCSVFieldnames(self) -> list:
        with open(self.csv_filepath) as csv_fname:
            self._logger.info(f"Attempting to automatically read fieldnames from {self.csv_filepath}.")
            try:
                csv_fields = [x.strip()
                              for x in csv_fname.readline().split(',')]
                if csv_fields is None or len(csv_fields) == 0:
                    try:
                        raise _FieldnamesAutoReadError("csv fieldnames could not be read.")
                    except _FieldnamesAutoReadError as e:
                        self._logger.error(e, exc_info=True)
                        raise e

                self._logger.info(f"Fieldnames successfully read from {self.csv_filepath}")
                self._logger.debug(f"CSV fields are - {csv_fields}")
            except _FieldnamesAutoReadError as e:
                self._logger.error(e, exc_info=True)

            csv_fname.close()
        return csv_fields

    def GetListDict(self) -> List[dict]:
        """Opens the CSV and reads it into a DictReader() then creates a list_dict and returns that."""
        self._logger.debug(f"csv file: {self.csv_filepath} with fieldnames: {self._fieldnames} entered to GetListDict")
        self._logger.info(f"getting list_dict from {self.csv_filepath}")
        # added encoding to deal with bug on 4/5/23
        with open(self.csv_filepath, encoding='utf-8') as csv_f:
            # YOU CANNOT USE CSV_F.READLINE BEFORE THE CHECK
            # OR THE COMPARISON WILL CHECK AGAINST LINE 2 AND WILL ALWAYS FAIL
            if [f.strip() for f in self._fieldnames] == [x.strip() for x in csv_f.readline().split(",")]:
                dictr = csv.DictReader(csv_f, fieldnames=self._fieldnames)
                self._logger.debug("DictReader Created")
                for row in dictr:
                    self.list_dict.append(row)
                    self._logger.debug(f"The following row was appended to list_dict {row}")
                self._logger.info(f"Returning list_dict with {len(self.list_dict)} entries")
                return self.list_dict
            else:
                try:
                    raise _FieldnamesMismatch("Make sure the CSV field names list chosen, matches the CSV chosen")
                except _FieldnamesMismatch as e:
                    self._logger.error(e, exc_info=True)
                    raise e
