import os
import unittest

import src.polus


def create_test_database():
    src.polus.create_database(database_path='test_polus.db')


def close_and_delete_test_database(*args):
    if args:
        args[0].close()
    os.remove('test_polus.db')


class TestPolusModules(unittest.TestCase):

    def test_create_database(self):
        # Creating test database
        create_test_database()

        # Asserting that database was created
        self.assertTrue(os.path.exists('test_polus.db'), msg='Database does not exist')

        # Close and delete test database
        close_and_delete_test_database()

    def test_table_creation(self):
        # Creating test database
        create_test_database()

        # Fetching column with name 'exhibits'
        conn, cur = src.polus.connect_to_database(database_path='test_polus.db')
        cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='exhibits'""")
        exhibits_table = cur.fetchone()[0]

        # Asserting that the exhibits table was returned
        self.assertTrue(exhibits_table == 'exhibits', msg='Exhibits table does not exist')

        # Close and delete test database
        close_and_delete_test_database(conn)

    def test_insert_data_into_database(self):
        # Creating test database
        create_test_database()

        # Declaring mock entries and inserting into test database
        database_path = 'test_polus.db'
        expected_id = src.polus.get_highest_id_number(database_path) + 1
        exhibit_details = src.polus.ExhibitDetails(
            case_id='12345',
            case_path='MOCK INPUT',
            exhibit='SJN/1',
            windows='Windows 11 Professional (2009)',
            mac='macOS 11.6.3',
            linux='Linux Mint 21.1 (Vera), Freedesktop SDK 22.08 (Flatpak runtime), '
                  'Ubuntu 22.04.2 LTS (Jammy Jellyfish)'
        )
        src.polus.insert_exhibit_to_database(database_path, exhibit_details)

        # Fetching mock exhibit details from test database
        conn, cur = src.polus.connect_to_database(database_path='test_polus.db')
        cur.execute("""SELECT * FROM exhibits""")
        entry = cur.fetchall()[0]
        entry_id = entry[0]
        entry_case_reference = entry[1]
        entry_path = entry[2]
        entry_exhibit_reference = entry[3]
        entry_windows_os_present = entry[4]
        entry_mac_os_present = entry[5]
        entry_linux_os_present = entry[6]

        # Asserting mock values are equivalent
        self.assertEqual(entry_id, expected_id,
                         msg=f'ID, expected {expected_id}, got {entry_id}')
        self.assertEqual(entry_case_reference, exhibit_details.case_id,
                         msg=f'Case, expected {exhibit_details.case_id}, got {entry_case_reference}')
        self.assertEqual(entry_path, exhibit_details.case_path,
                         msg=f'Case, expected {exhibit_details.case_path}, got {entry_path}')
        self.assertEqual(entry_exhibit_reference, exhibit_details.exhibit,
                         msg=f'Exhibit, expected {exhibit_details.exhibit}, got {entry_exhibit_reference}')
        self.assertEqual(entry_windows_os_present, exhibit_details.windows,
                         msg=f'WindowsOS, expected {exhibit_details.windows}, got {entry_windows_os_present}')
        self.assertEqual(entry_mac_os_present, exhibit_details.mac,
                         msg=f'MacOS, expected {exhibit_details.mac}, got {entry_mac_os_present}')
        self.assertEqual(entry_linux_os_present, exhibit_details.linux,
                         msg=f'LinuxOS, expected {exhibit_details.linux}, got {entry_linux_os_present}')

        # Close and delete test database
        close_and_delete_test_database(conn)

    def test_windows_os(self):
        windows_test_database = os.path.join(dfs_polus_directory, 'rsc', 'Windows', 'Case.mfdb')

        os_installations = src.polus.get_case_number_and_exhibit_details(windows_test_database)

        os_installations_expected = 'Windows 11 Professional (2009)'

        self.assertEqual(os_installations_expected, os_installations.windows,
                         msg=f'Expected: {os_installations_expected}\nActual: {os_installations.windows}')

    def test_mac_os(self):
        mac_test_database = os.path.join(dfs_polus_directory, 'rsc', 'macOS', 'Case.mfdb')

        os_installations = src.polus.get_case_number_and_exhibit_details(mac_test_database)

        os_installations_expected = 'macOS 11.6.3'

        self.assertEqual(os_installations_expected, os_installations.mac,
                         msg=f'Expected: {os_installations_expected}\nActual: {os_installations.mac}')

    def test_linux_os(self):
        linux_test_database = os.path.join(dfs_polus_directory, 'rsc', 'Linux', 'Case.mfdb')

        os_installations = src.polus.get_case_number_and_exhibit_details(linux_test_database)

        os_installations_expected = ('Windows 10 Home (2009),Linux Mint 21.1 (Vera),Freedesktop SDK 22.08 (Flatpak '
                                     'runtime),Ubuntu 22.04.2 LTS (Jammy Jellyfish)')
        os_installations = f'{os_installations.windows},{os_installations.linux}'
        self.assertEqual(os_installations_expected, os_installations,
                         msg=f'Expected: {os_installations_expected}\nActual: {os_installations}')

    def test_get_cases_and_paths(self):
        rsc_directory = os.path.join(dfs_polus_directory, 'rsc')
        cases_and_paths = src.polus.get_cases_and_paths(rsc_directory)

        linux = cases_and_paths[0].path
        mac = cases_and_paths[1].path
        windows = cases_and_paths[2].path

        self.assertEqual(linux, 'C:\\Users\\DFU\\PycharmProjects\\DFSPolus\\rsc\\Linux\\Case.mfdb')
        self.assertEqual(mac, 'C:\\Users\\DFU\\PycharmProjects\\DFSPolus\\rsc\\macOS\\Case.mfdb')
        self.assertEqual(windows, 'C:\\Users\\DFU\\PycharmProjects\\DFSPolus\\rsc\\Windows\\Case.mfdb')


class TestPolus(unittest.TestCase):
    def test_polus(self):
        src.polus.run_polus(polus_db_path='test_polus.db',
                            rsc_path='C:\\Users\\DFU\\PycharmProjects\\DFSPolus\\rsc')

        close_and_delete_test_database()


dfs_polus_directory = str(os.path.abspath(os.path.dirname(__file__))).replace('\\test_src', '').replace(
    '\\test_polus.py', '')
