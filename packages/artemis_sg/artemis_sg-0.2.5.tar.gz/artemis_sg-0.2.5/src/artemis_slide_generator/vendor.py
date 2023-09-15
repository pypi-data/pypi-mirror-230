# -*- coding: utf-8 -*-

import json
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()


class Vendor:
    def __init__(self, code):
        self.vendor_code = code
        self.vendor_name = ""
        self.isbn_key = ""

    def _get_database_data(self):
        namespace = f"{type(self).__name__}.{self._get_database_data.__name__}"

        logging.info(f"{namespace}: Fetch vendor database")
        database = os.environ["ASG_VENDOR_DATAFILE"]
        logging.debug(f"{namespace}: Vendor database: {database}")
        try:
            with open(database, encoding="utf-8") as f:
                data = json.load(f)
            f.close()
        except FileNotFoundError:
            logging.error(f"{namespace}: Database file not found.")
            sys.exit(1)
        return data

    def _filter_database_data(self, all_data):
        namespace = f"{type(self).__name__}.{self._filter_database_data.__name__}"
        try:
            return all_data[self.vendor_code]
        except KeyError:
            logging.error(f"{namespace}: Vendor code not found in database")
            sys.exit(1)

    def set_vendor_data(self):
        """Create Vendor object class"""
        namespace = f"{type(self).__name__}.{self.set_vendor_data.__name__}"

        all_data = self._get_database_data()
        vendor_data = self._filter_database_data(all_data)
        logging.debug(f"{namespace}: Vendor data is: '{vendor_data}'")
        self.vendor_name = vendor_data["name"]
        self.isbn_key = vendor_data["isbn_key"].upper()
