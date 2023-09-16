import argparse
import json
import logging
import os
import sys
from os.path import basename

import jsonschema

import igs_toolbox
from igs_toolbox.formatChecker.seq_metadata_schema import seqMetadata

SCHEMA_NAME = "seqMetadata"


def validateSpecies(pathogen, species):
    # get vocabulary for species
    dirname = os.path.dirname(__file__)
    pathToAnswerSet = os.path.join(dirname, f'res/species/txt/answerSet{pathogen}.txt')
    if not os.path.isfile(pathToAnswerSet):
        logging.error(f"{pathToAnswerSet} does not point to a file. Aborting.")
        return False

    with open(pathToAnswerSet, "r") as speciesfile:
        speciesList = [line.strip() for line in speciesfile]

    if species not in speciesList:
        logging.error(f"{species} is not a valid species for pathogen {pathogen}.")
        return False
    return True

def checkSeqMetadata(jsonData):
    validator = jsonschema.Draft202012Validator(seqMetadata)
    errors = list(validator.iter_errors(jsonData))
    if errors:
        for error in errors:
            error_location = " -> ".join(error.absolute_path)
            logging.error(f"{error_location}: {error.message}")
        return False

    # some validation rules cannot be implemented in jsonschema directly, thus check them here programmatically
    if "SPECIES" in jsonData.keys() and  not validateSpecies(jsonData["MELDETATBESTAND"], jsonData["SPECIES"]):
        return False
    return True

# Read command line arguments
def parse(args=None):

    parser = argparse.ArgumentParser(prog=basename(__file__).split(".")[0])
    parser.add_argument('-i', '--input', required=True, help="Filepath to json file.")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {igs_toolbox.__version__}")
    args = parser.parse_args(args)
    return args

def main(args=None):
    input_file = parse(args).input
    # read json file
    if not os.path.isfile(input_file):
        logging.error(f"{input_file} does not point to a file. Aborting.")
        sys.exit(1)

    with open(input_file, "r") as jsonfile:
        try:
            jsonData = json.loads(jsonfile.read())
        except json.decoder.JSONDecodeError:
            logging.error(f"{input_file} is not a valid json file. Aborting.")
            sys.exit(1)

    # get schema
    if not checkSeqMetadata(jsonData):
        logging.error(f"FAILURE: JSON file does not adhere to the {SCHEMA_NAME} schema.")
        sys.exit(1)

    logging.info(f"SUCCESS: JSON file adheres to {SCHEMA_NAME} schema.")
    print(f"SUCCESS: JSON file {input_file} adheres to {SCHEMA_NAME} schema.")

if __name__ == "__main__":
    main()
