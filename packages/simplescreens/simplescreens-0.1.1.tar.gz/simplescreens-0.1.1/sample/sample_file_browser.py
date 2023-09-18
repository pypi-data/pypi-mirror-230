import sys
from os import listdir
from os.path import isfile, join

from simplescreens import *

#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def get_folder_or_file_details (params: dict) -> tuple:
    file_or_folder = params['title']
    result = []
    if isfile(file_or_folder):
        return (f'{file_or_folder} (file info)', f'These are details of a file: {file_or_folder}', [])
    else:
        content = listdir(f'{file_or_folder}\\')
        for ff in content:
            item = {}
            item['title'] = f'{file_or_folder}\\{ff}'
            item['details_function'] = get_folder_or_file_details
            result.append(item)
        return (file_or_folder, '', result)

def build_root_params() -> dict:
    root = {}
    root['title'] = 'C:'
    root['details_function'] = get_folder_or_file_details    
    return root

def main () -> int:
    try:
        root_params = build_root_params()
        start_walking(' Welcome', 'Thank you!', root_params)
        return 0
    except Exception as e:
        print(str(e))
        return 1
    
if __name__ == "__main__":
    sys.exit (main ())

