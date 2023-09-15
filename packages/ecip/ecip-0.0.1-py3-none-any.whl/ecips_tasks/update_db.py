from datetime import datetime, timedelta
import argparse
import glob
import os
import pathlib
import shutil
import logging


def main(ecips_db, days):
    ecips_database = str(ecips_db)
    keep_days = int(days)

    logging.debug("Finding today's date")
    today = datetime.today()

    logging.debug('Gathering files and dirs from ecips_db to be removed from database')

    date_list = [today - timedelta(days=x) for x in range(keep_days)]
    for date in date_list:
        year = date.year
        month = date.month
        day = date.day
        date_path = f'year={year}/month={month}/day={day}'
        if date == date_list[0]:
            keep_items = glob.glob(ecips_database + f'/**/{date_path}/*.parquet')
            keep_items.extend(glob.glob(ecips_database + f'/**/{date_path}'))
        else:
            keep_items.extend(glob.glob(ecips_database + f'/**/{date_path}/*.parquet'))
            keep_items.extend(glob.glob(ecips_database + f'/**/{date_path}'))

    paths = glob.glob('/mnt/database/ecips_db/*/*/*/*')
    paths.extend(glob.glob('/mnt/database/ecips_db/*/*/*/*/*.parquet'))

    rm_items = [item for item in paths if item not in keep_items]

    logging.debug('Deleting old files and directories')
    for item in rm_items:
        try:
            if os.path.isfile(item):
                os.remove(item)
            else:
                shutil.rmtree(item)
        except FileNotFoundError:
            pass


if __name__ == 'main':
    parser = argparse.ArgumentParser(description='')  # NOSONAR
    # - Beyond type formatting which is checked in the parsing below before use,
    # there are no requirements for actual input values
    parser.add_argument('-db', '--db', type=pathlib.Path, help='Database path', required=True)
    parser.add_argument('-days', '--days', type=int, help='Days to keep', required=True)
    args = vars(parser.parse_args())
    main(args['db'], args['days'])
