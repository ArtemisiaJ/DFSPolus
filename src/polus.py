"""
@name:      DFS Polus
@author:    PSE 61715 JACKSON-NICHOLS
@email:     61715@kent.police.uk
@date:      23/02/2024
"""


########################################################################################################################
# Importing Modules
########################################################################################################################

import re
import sqlite3
import os
import sys


########################################################################################################################
# Declaring Class Attributes
########################################################################################################################

class ExhibitDetails:
    def __init__(self, case_id, case_path, exhibit, windows, mac, linux):
        self.case_id = case_id
        self.case_path = case_path
        self.exhibit = exhibit
        self.windows = windows
        self.mac = mac
        self.linux = linux


class CasePaths:
    def __init__(self, case_id, path, valid):
        self.case_id = case_id
        self.path = path
        self.valid = valid


########################################################################################################################
# Creating Polus Database
########################################################################################################################


def connect_to_database(database_path):
    # Connect to the database and create a cursor
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    return conn, cur


def create_database(database_path):
    # Get connection and cursor
    conn, cur = connect_to_database(database_path)

    # Create exhibits table
    cur.execute("""CREATE TABLE IF NOT EXISTS exhibits (
        id INTEGER PRIMARY KEY,
        case_id VARCHAR(50),
        case_path VARCHAR(500),
        exhibit VARCHAR(50),
        windows VARCHAR(800),
        mac VARCHAR(800),
        linux VARCHAR(800)
    )""")

    # Commit changes
    conn.commit()

    # Close database connection
    conn.close()


########################################################################################################################
# Interacting with Polus Database
########################################################################################################################

def get_highest_id_number(database_path):
    # Get connection and cursor
    conn, cur = connect_to_database(database_path)
    number_list = []

    cur.execute("""SELECT id FROM exhibits""")
    ids = cur.fetchall()
    for id_list in ids:
        for number in id_list:
            number_list.append(number)

    try:
        highest_number = max(number_list)
    except ValueError:
        highest_number = 0

    conn.close()
    return highest_number


def insert_exhibit_to_database(polus_database_path, exhibit_details):
    entry_id = get_highest_id_number(polus_database_path) + 1
    conn, cur = connect_to_database(polus_database_path)
    cur.execute(f"""
    INSERT INTO exhibits (id, case_id, case_path, exhibit, windows, mac, linux) 
    VALUES ('{entry_id}', '{exhibit_details.case_id}', '{exhibit_details.case_path}', '{exhibit_details.exhibit}',
    '{exhibit_details.windows}', '{exhibit_details.mac}', '{exhibit_details.linux}')""")
    conn.commit()
    conn.close()


########################################################################################################################
# Get OS details
########################################################################################################################

def get_case_number_and_exhibit_details(extraction_database_path):
    # Connecting to database
    conn = sqlite3.connect(extraction_database_path)
    cur = conn.cursor()

    # Obtaining case_number entry, which will be both case_id and exhibit
    cur.execute("""SELECT case_number FROM case_info""")
    case_id_and_exhibit = str(cur.fetchone()[0]).replace(' ', '')

    # Declaring regex for case_id and exhibit
    case_id_regex = re.compile('[0-9]{1,6}-[0-9]{2,3}')
    exhibit_regex = re.compile('[a-zA-Z]+-[0-9]+')

    # Determining case_id and exhibit
    try:
        case_id = case_id_regex.findall(case_id_and_exhibit)[0]
        exhibit = exhibit_regex.findall(case_id_and_exhibit)[0]
    except IndexError:
        print("No case")
        case_id = None
        exhibit = None
        pass

    # Windows
    cur.execute("""
    SELECT fragment_definition.fragment_definition_id, fragment_definition.name, hit_fragment.value,
    hit_fragment.fragment_definition_id
    
    FROM fragment_definition
    INNER JOIN hit_fragment 
    ON fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id
    
    WHERE fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id 
    AND fragment_definition.name = 'Operating System'
    AND hit_fragment.value LIKE '%Windows%'
    AND hit_fragment.value NOT LIKE '%OS X%'
    """)

    windows = cur.fetchall()

    # Mac
    cur.execute("""
    SELECT fragment_definition.fragment_definition_id, fragment_definition.name, hit_fragment.value,
    hit_fragment.fragment_definition_id

    FROM fragment_definition
    INNER JOIN hit_fragment 
    ON fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id

    WHERE fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id 
    AND fragment_definition.name = 'Operating System'
    AND hit_fragment.value NOT LIKE '%Windows%'
    AND hit_fragment.value LIKE '%macOS%'
    AND hit_fragment.value != 'Core'

    OR fragment_definition.name = 'Version Number'
    AND hit_fragment.value NOT LIKE '%Windows%'
    AND hit_fragment.value != 'Core'
    """)

    mac = cur.fetchall()

    # Linux
    cur.execute("""
    SELECT fragment_definition.fragment_definition_id, fragment_definition.name, hit_fragment.value,
    hit_fragment.fragment_definition_id

    FROM fragment_definition
    INNER JOIN hit_fragment 
    ON fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id

    WHERE fragment_definition.fragment_definition_id = hit_fragment.fragment_definition_id 
    AND fragment_definition.name = 'Operating System'
    AND hit_fragment.value NOT LIKE '%Windows%'
    AND hit_fragment.value NOT LIKE '%macOS%'
    AND hit_fragment.value != 'Core'
    
    OR fragment_definition.name = 'Operating System Version'
    AND hit_fragment.value NOT LIKE '%Windows%'
    AND hit_fragment.value NOT LIKE '%macOS%'
    AND hit_fragment.value != 'Core'
    """)

    linux = list(dict.fromkeys(cur.fetchall()))

    conn.close()

    # Consolidating Windows installations
    if len(windows) < 1:
        windows_installations = None
    else:
        windows_installations = []
        for a, b, c, d in windows:
            windows_installations.append(c)
        windows_installations = ','.join(map(str, windows_installations))

    # Consolidating Mac installations
    if len(mac) < 2:
        mac_installations = None
    else:
        mac_installations = consolidate_installations(mac)
        mac_installations = ','.join(map(str, mac_installations))

    # Consolidating Linux installations
    if len(linux) < 2:
        linux_installations = None
    else:
        linux_installations = consolidate_installations(linux)
        linux_installations = ','.join(map(str, linux_installations))

    exhibit_details = ExhibitDetails(
        case_id=case_id,
        case_path=extraction_database_path,
        exhibit=exhibit,
        windows=windows_installations,
        mac=mac_installations,
        linux=linux_installations
    )

    return exhibit_details


def consolidate_installations(database_output):
    current = 0
    consolidated_installations = []
    installation_count = int(len(database_output) / 2)
    while current < installation_count:
        consolidated_installations.append(f'{database_output[current][2].replace('"', '')} '
                                          f'{database_output[current + installation_count][2].replace('"', '')}')
        current += 1

    return consolidated_installations


########################################################################################################################
# Get cases
########################################################################################################################

def get_cases_and_paths(path):
    cases_and_paths_list = []

    for folder in next(os.walk(path))[1]:
        full_path = os.path.join(path, folder)
        try:
            case_id = int(folder[:5])
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if file.endswith('.mfdb'):
                        case_and_path = CasePaths(case_id, full_path, valid=True)
                        cases_and_paths_list.append(case_and_path)

        except ValueError:
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if file.endswith('.mfdb'):
                        temp_var = os.path.join(full_path, file)
                        case_and_path = CasePaths(folder, temp_var, valid=True)
                        cases_and_paths_list.append(case_and_path)

    return cases_and_paths_list


########################################################################################################################
# Launch Script
########################################################################################################################

def run_polus(polus_db_path, rsc_path):
    polus_db_path = os.path.join(polus_db_path, 'polus.db')
    create_database(polus_db_path)
    if rsc_path is not None:
        rsc_directory = rsc_path
    else:
        rsc_directory = input('Enter path to scan for .mfdb files:\n')
    cases_and_paths = get_cases_and_paths(rsc_directory)
    print(f'Cases found: {len(cases_and_paths)}\n')

    for case in cases_and_paths:
        if case.valid:
            os_installations = get_case_number_and_exhibit_details(case.path)
            if os_installations.case_id is None:
                if case.case_id is None:
                    case_id = 0
                else:
                    case_id = case.path.split('')
            else:
                case_id = os_installations.case_id
            case_path = case.path
            print(f'Processing case {case_id}!\nPath: {case_path}')
            exhibit = os_installations.exhibit
            windows = os_installations.windows
            mac = os_installations.mac
            linux = os_installations.linux

            insert_exhibit_to_database(polus_db_path, exhibit_details=ExhibitDetails(
                case_id=case_id,
                case_path=case_path,
                exhibit=exhibit,
                windows=windows,
                mac=mac,
                linux=linux
            ))

            print(f'Finished processing case {case_id}!\n')

        else:
            print(f'{case.case_id} is not valid!\n{case.path}\n\n')
    input('Processing complete!\nPress any key to exit the program...')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):
            run_polus(sys.argv[1], sys.argv[2])
        else:
            print('Invalid arguments! Insert manually or check entries\n')
    else:
        run_polus(polus_db_path=input(f'\nEnter path to save polus database:\n'),
                  rsc_path=input(f'\nEnter path to scan for .mfdb files:\n'))


# polus "C:\Users\DFU\PycharmProjects\DFSPolus\Test" "C:\Users\DFU\PycharmProjects\DFSPolus\rsc"
