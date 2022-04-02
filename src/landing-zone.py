
import os
import re
from pyarrow import json, csv
import pyarrow.parquet as pq
from hdfs import InsecureClient

# Define our global variables. TEMPORAL_DIR is the temporary landing zone where raw files will be placed that need
# to be processed PERSISTENT_DIR will be the location of files converted to the selected file format

TEMPORAL_DIR = '../data/raw'
PERSISTENT_DIR = '../data/processed'
HDFS_DIR = '.'
client = InsecureClient('http://10.4.41.37:9870', user='bdm')  # this IP should be changed to your personal VM


def convert_to_parquet(file_type, in_directory, in_filename, out_directory, out_filename):
    '''
    This function will take an input file in the form of CSV from a given directory,
    convert the file to a parquet, and place the file in a directory specified in parameters.

    :param file_type:
    :param in_directory: directory where the CSV file exists
    :param in_filename: filename (including extension) that will be converted into parquet file
    :param out_directory: directory where the parquet file should be placed after conversion
    :param out_filename: filename that will be given to converted parquet file
    :return: None
    '''
    if file_type == "json":
        table = json.read_json(f'{in_directory}/{in_filename}')
        pq.write_table(table, f'{out_directory}/{out_filename}')
    elif file_type == "csv":
        table = csv.read_csv(f'{in_directory}/{in_filename}')
        pq.write_table(table, f'{out_directory}/{out_filename}')


# First we can strip primary metadata information from the filename as received from the website.
# TODO: move original file into same folder as new .parquet
# TODO: create new directories in parquet without overwriting
# TODO: add instructions to setup file
def create_persistent_directory():
    for filename in os.listdir(TEMPORAL_DIR):  # iterate over all files in directory DIR
        if not filename.startswith('.'):  # do not process hidden files that start with "."
            metadata = re.split('[-.]', filename)  # splits the filename on '-' and '.' -> creates a list
            file_directory = f"{PERSISTENT_DIR}/{metadata[0]}/{metadata[1]}"  # uses YYYY/MM as the name of the sub-directory
            new_filename = f"{metadata[3]}-{metadata[4]}-{metadata[5]}"  # new file name will be userID-taskID
            if not os.path.exists(file_directory):  # creates the directory if it doesn't exist
                os.makedirs(file_directory)
            file_type = metadata[6]
            convert_to_parquet(file_type, TEMPORAL_DIR, filename, file_directory, new_filename)


def move_to_hdfs(temporal_path, persistent_path):
    client.upload(persistent_path, temporal_path)


if __name__ == '__main__':
#    create_persistent_directory()
#    move_to_hdfs(PERSISTENT_DIR, HDFS_DIR)
# this line of code will move this single file to user/bdm in virtual machine
    client.upload('.', '../data/processed/2022/03/ABR001-002-AB12')
    print(client.status('.'))
    print(client.resolve('.'))
    print(f"I'm done!")