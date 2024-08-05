import argparse
import sys
import logging
import os
import shutil


def checkPathNeeded():
    """ Checks if any of the file addition or remove arguments are present """
    return bool(
        set({"-a", "--add", "-rm", "--remove"}).intersection(set(sys.argv))
    )


parser = argparse.ArgumentParser(
    prog="Onefile",
    description="The simple, selhosted way of distributing files."
)

parser.add_argument(
    "-p",
    "--path",
    help="Path to file",
    required=checkPathNeeded(),
    default=""
)

parser.add_argument(
    "-a",
    "--add",
    help="Add a new file to Onefile",
    action="store_true",
)

parser.add_argument(
    "-rm",
    "--remove",
    help="Remove a file from Onefile",
    action="store_true"
)


if __name__ == "__main__":
    args = parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)

    # XORing checks if both are present or none is present
    if not (args.add ^ args.remove):
        if args.add:
            logging.error("Adding and removing file has been specified.")
        else:
            logging.error("Need to specify either adding or removing a file")
        exit()

    # If we are adding a file, path is file path, if deleting path is now
    # just a filename in the shared_files directory
    if not os.path.isfile(args.path) and args.add:
        logging.error("A valid path needs to be specified.")
        exit()

    if args.add:
        logging.info("File is being added")
        shutil.copy(args.path, os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "shared_files/",
        )))

    if args.remove:
        pathToFile = os.path.join(
            os.path.dirname(__file__), "..", "shared_files/", args.path
        )
        # Check if file is in shared_files directory
        if not os.path.isfile(pathToFile):
            logging.error("File is not in Onefile shared directory")
            exit()

        logging.info("File is being removed")
        os.remove(pathToFile)
