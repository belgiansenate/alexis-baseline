"""
    This file contains the starting point of the application (main)
"""

import argparse
import configparser
import os
import subprocess


def launch_first_install_process(limit=None):
    print("First install. Launching store_passage.py...")
    if limit is None:
        subprocess.run(['python', 'store_passages.py'])
    else:
        subprocess.run(['python', 'store_passages.py', '--limit', str(limit)])


def launch_subsequent_install_process():
    print("Launching dev_gui.py...")
    subprocess.run(['python', 'dev_gui.py'], env=os.environ.copy())


def check_first_install(limit):
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if not os.path.exists('config.ini'):
        # If it doesn't exist, it's the first install
        launch_first_install_process(limit)

        # Create the configuration file and set the flag to False
        config['Installation'] = {'FirstInstall': 'False'}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        # The configuration file exists, check if it's the first install
        config.read('config.ini')
        first_install = config['Installation'].getboolean('FirstInstall')

        if first_install:
            # It's the first install, run the process
            launch_first_install_process(limit)

            # Update the flag to indicate that the process has been run
            config['Installation']['FirstInstall'] = 'False'
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        else:
            # It's not the first install
            launch_subsequent_install_process()


if __name__ == '__main__':
    # Create the argument parser
    parser = argparse.ArgumentParser()

    # Add the argument for the variable
    parser.add_argument("--limit", type=int, help="Specify the limit of records to store in the database")

    # Parse the command-line arguments
    args = parser.parse_args()

    check_first_install(limit=args.limit)
    launch_subsequent_install_process()
