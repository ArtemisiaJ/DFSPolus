from datetime import datetime
import os
import shutil
from threading import Thread


# Transfers data within a separate thread
def transfer_thread(current_path: str, new_path: str):
    # Declares file path (excluding file name and extension) and creates the path, so it is ready for file transfer
    new_path_without_file = new_path.rsplit('\\', 1)[0]
    try:
        os.makedirs(new_path_without_file)
    except Exception as e:
        print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
              f'Exception: {e}\n'
              f'Path ({new_path_without_file}) already exists!\n')
        pass

    # Starts file transfer
    try:
        shutil.copyfile(current_path, new_path)
        print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
              f'A transfer has completed: {new_path}\n')
    except Exception as e:
        print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
              f'Exception: {e}\n'
              f'File ({new_path_without_file}) already exists!\n')


# Scans source_directory for any mfdb files
def scan_for_mfdb_files(source_directory: str):
    # Directories that the script will skip
    root_folders_to_skip = [
        '#Lab scanner',
        'Workstation Builds',
        'Viewing Room',
        'Validation',
        'UKAS 2023',
        'Testing',
        'temp_extraction_path',
        'TD3 Log',
        'Servers',
        'SCD Outputs',
        'S-21 Training (TEMP)',
        'Ref Media Audit',
        'Python',
        'Premium',
        'NAT-D1-SSD',
        'Natalie D Drive',
        'FLOPPY LOADER',
        'DFUSCD4128',
        'DB Backup',
        'Commander',
        'Cellebrite Automation',
        'CCTV',
        'BING TEST',
        'ADF TRAINING',
        'ADF DEI Imager v2.7.0.43 Audit'
    ]
    further_folders_to_skip = [
        'pictures',
        'Pictures',
        'Griffeye',
        'Converted',
        'videos',
        'Videos'
    ]

    # Declares destination directory and creates if not exists
    d_isilon_scans_dir = 'D:\\isilon_scans'
    if not os.path.exists(d_isilon_scans_dir):
        os.makedirs(d_isilon_scans_dir)

    # Walks source_directory
    for root, dirs, files in os.walk(source_directory):

        # Checks if root folders are to be skipped
        root_check = root.rsplit('\\', 1)[1]
        if root_check not in root_folders_to_skip:

            # Iterates through files
            for file in files:

                # Checks if files are to be skipped
                if not any(further_folders_to_skip) in dirs:

                    # Checks if files have '.mfdb' extension
                    if '.mfdb' in file:

                        # Declares current and new paths
                        current_path = f'{root}\\{file}'
                        new_path = current_path.replace('U:\\', 'D:\\isilon_scans')

                        # Attempts to start file transfer from current to new path
                        try:
                            Thread(target=transfer_thread, args=(current_path, new_path)).start()
                            print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
                                  f'Located .mfdb file, started transfer.\n'
                                  f'Current Path: {current_path}\n'
                                  f'New Path: {new_path}\n')

                        # Catches exceptions that occur
                        except Exception as e:
                            print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
                                  f'Exception: {e}, file not transferred!\n'
                                  f'Current Path: {current_path}\n')
                            pass

        else:
            # Declares if root folder has been skipped
            print(f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}\n'
                  f'Skipped: {root}')


if __name__ == '__main__':
    # User input for source, and asserts that is a folder
    source = input('Path to copy from\n')
    assert os.path.isdir(source)

    # Scans and transfers files
    scan_for_mfdb_files(source)
