import argparse
import json
import os

import pkg_resources  # part of setuptools
version = pkg_resources.require("fileformattools")[0].version

# Read command line arguments
def parse():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help="Filepath to folder with answerset json files.")
    parser.add_argument('-o', '--output', required=True,
                        help="Filepath to output folder for answerset txt files.")
    parser.add_argument('-s', '--species', nargs='+', help="List of species for which to convert answersets.", default=[
                        "EHCP", "LISP", "SALP", "STYP", "INVP", "NEIP", "MSVP", "MYTP", "CVDP", "HIVP", "NEGP", "EBCP", "ACBP", "CDFP", "MRAP", "SALP", "HEVP", "HAVP", "LEGP", "SPNP", "WNVP"])       
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=version))
    args = parser.parse_args()
    return args


def convertAnswerset(observation, input, output):
    # get vocabulary for species
    pathToAnswerSet = os.path.join(input, f"answerSet{observation}.json")
    if not os.path.isfile(pathToAnswerSet):
        print(f"{pathToAnswerSet} does not point to a file. Aborting.")
        return

    with open(pathToAnswerSet, "r") as jsonfile:
        try:
            answerset = json.loads(jsonfile.read())
        except json.decoder.JSONDecodeError:
            print(f"{pathToAnswerSet} is not a valid json file. Aborting.")
            return
    answersetList = [species["display"]
                     for species in answerset["compose"]["include"][0]["concept"]]

    # open file in write mode
    with open(os.path.join(output, f"answerSet{observation}.txt"), 'w') as fp:
        for item in answersetList:
            # write each item on a new line
            fp.write(f"{item}\n")
        print(f'Converted {pathToAnswerSet}')


def main():
    args = parse()
    os.makedirs(args.output, exist_ok=True)
    for obs in args.species:
        convertAnswerset(obs, args.input, args.output)


if __name__ == "__main__":
    main()
