import os
import zipfile
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory",
                        help="""
                                Directory path to image zip files downloaded from webapat corresponding
                                Example: ~/Downloads/webapat/IMAGES
                             """
                        )

    args = parser.parse_args()

    for item in os.listdir(args.directory):
        if item.endswith(".zip"):
            file_name = os.path.abspath(item)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(args.directory)
            zip_ref.close()
            os.remove(file_name)
