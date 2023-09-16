import argparse
import json
import logging
import os
import sys
from datetime import datetime

import pandas as pd

import pkg_resources  # part of setuptools
version = pkg_resources.require("fileformattools")[0].version

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from igs_toolbox.formatChecker import jsonChecker


# Read command line arguments
def parse():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help="Filepath to xlsx file.")
    parser.add_argument('-o', '--output', required=True, help="Filepath to output folder for json files.")
    parser.add_argument('-e', '--error_log', required=False, help="Filepath to log file.", default=datetime.now().strftime("%d%m%Y%H%M%S")+".log")
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=version))
    args = parser.parse_args()
    return args

def main():
    args = parse()
    logging.basicConfig(filename=args.error_log, encoding='utf-8', level=logging.ERROR, format="%(message)s")
    # read json file
    if not os.path.isfile(args.input):
        print(f"{args.input} does not point to a file. Aborting.")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    meta_df = pd.read_excel(args.input, dtype=str)
    meta_dict = meta_df.to_dict(orient="records")
    for entry_dict in meta_dict:
        sample_id = entry_dict["LAB_SEQUENCE_ID"]
         # replace NANs
        clean_dict =  {k: entry_dict[k] for k in entry_dict if not pd.isna(entry_dict[k])}
        if jsonChecker.checkSeqMetadata(clean_dict):
            with open(os.path.join(args.output, sample_id+"_sequencing_metadata.json"), "w") as outfile:
                json.dump(clean_dict, outfile, indent=4)


if __name__ == "__main__":
    main()
