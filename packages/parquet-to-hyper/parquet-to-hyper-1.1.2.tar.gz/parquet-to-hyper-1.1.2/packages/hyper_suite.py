from tableauhyperapi import SqlType, TableDefinition, NULLABLE, TableName, HyperProcess, Telemetry, \
    Connection, CreateMode, escape_name
from pathlib import Path
from packages.time_decorator import timeit
from pyarrow import ChunkedArray
from pyarrow.parquet import ParquetFile
import pyarrow as pa
import os
import subprocess
import logging
import argparse

class GCSFuse:

    def __init__(self, bucket_name : str, mnt_dir : str) -> None:
        """

        Args:
            bucket_name (str): bucket name
            mnt_dir (str): path where the bucket will be mounted
        """
        self.bucket_name = bucket_name
        self.mnt_dir = mnt_dir

    def mount(self) -> None:
        """Mount GCS bucket as a path on the machine"""
        os.makedirs(self.mnt_dir, exist_ok=True)
        exec = subprocess.run(['gcsfuse', '--implicit-dirs', self.bucket_name, self.mnt_dir],
                stdout=subprocess.DEVNULL)
        if exec.returncode != 0:
            raise ValueError(f'The mount command returned error {exec.returncode}. Check the whether the \
                bucket {self.bucket_name} or the mount dir {self.mnt_dir} is correct.')
        return exec.returncode


class HyperSuite:

    def __init__(self, bucket_name : str, parquet_dir : str, hyper_db_path : str) -> None:
        self.bucket_name = bucket_name
        self.parquet_dir = parquet_dir
        self.hyper_db_path = hyper_db_path
        self.g_fuse = GCSFuse(bucket_name, './gcs/')
        self.filenames = self._get_filenames()

    def _get_filenames(self) -> list[str]:
        gcs_path = f'gs://{self.bucket_name}/{self.parquet_dir}/'
        process = subprocess.run(['gsutil', 'ls', gcs_path], shell=True, capture_output=True, text=True)
        filenames = [os.path.basename(path) for path in process.stdout.splitlines()]
        if len(filenames) == 0:
            raise ValueError(f'Error! The bucket path {gcs_path} returned no files!')
        return filenames

    def copy_parquet_to_hyper_file(self) -> None:
        """Function that copies data from a Parquet file to a .hyper file."""
        if os.path.exists(self.hyper_db_path):
            os.remove(self.hyper_db_path)
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
            with Connection(endpoint=hp.endpoint,
                            database=Path(self.hyper_db_path + '.hyper'),
                            create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
                table_definition = self._get_table_def(ParquetFile(self.filenames[0]))
                connection.catalog.create_schema(schema=table_definition.table_name.schema_name)
                connection.catalog.create_table(table_definition=table_definition)
                total_rows = 0
                for parquet_path in self.filenames:
                    try:
                        self.g_fuse.mount()
                        copy_command = f"COPY \"Extract\".\"Extract\" from '{parquet_path}' with (format parquet)"
                        count = connection.execute_command(copy_command)
                        total_rows += count
                    except Exception:
                        logging.warning(f'File {os.path.basename(parquet_path)} is empty.')
                logging.info(f'Process completed with {total_rows} rows added.')
                return total_rows

    def delete_rows_from_hyper_file(self, days_to_delete : int, date_column : str) -> None:
        """Function that copies data from a Parquet file to a .hyper file.

        Args:
            days_to_delete (int): the window in days to be deleted from the database
            date_column (str): name of date column to be used in the incremental strategy
        """
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
            with Connection(endpoint=hp.endpoint,
                            database=Path(self.hyper_db_path),
                            create_mode=CreateMode.NONE) as connection:
                self.g_fuse.mount()
                delete_command = f'DELETE FROM \"Extract\".\"Extract\" WHERE {escape_name(date_column)} >= CURRENT_DATE - {days_to_delete}'
                count = connection.execute_command(delete_command)
                logging.info(f'Process completed with {count} rows deleted.')

    def insert_hyper_records(self) -> None:
        """Function to insert records to an existing hyper file"""
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
            with Connection(endpoint=hp.endpoint,
                            database=Path(self.hyper_db_path),
                            create_mode=CreateMode.NONE) as connection:
                total_rows = 0
                for parquet_path in self.parquet_dir:
                    try:
                        self.g_fuse.mount()
                        copy_command = f"COPY \"Extract\".\"Extract\" from '{parquet_path}' with (format parquet)"
                        count = connection.execute_command(copy_command)
                        total_rows += count
                    except Exception as e:
                        logging.warning(f'File {os.path.basename(parquet_path)} is empty.')
                logging.info(f'Process completed with {total_rows} rows added.')

@timeit
def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting create single hyper process.')

    CLI = argparse.ArgumentParser()
    CLI.add_argument('--parquet_folder_path', type=str)
    CLI.add_argument('--bucket_name', type=str)
    CLI.add_argument('--hyper_file_path', type=str)
    CLI.add_argument('--days_to_delete', type=int, default=1)
    CLI.add_argument('--date_column', type=str, default='')
    CLI.add_argument('--func', type=str, default='incremental')
    args = CLI.parse_args()

    parquet_folder  = args.parquet_folder_path   #'PARQUET_1'
    bucket_name     = args.bucket_name          #'br-apps-dolphin-ddp-dev-comercial'
    hyper_file_path = args.hyper_file_path      #'/mnt/daily_sales.hyper'
    days_to_delete  = args.days_to_delete       #30
    date_column     = args.date_column          # DATE_KEY
    func            = args.func                 # full/incremental

    hs = HyperSuite(bucket_name, parquet_folder, hyper_file_path)
    if func == 'full':
        hs.copy_parquet_to_hyper_file()
    elif func == 'incremental':
        hs.delete_rows_from_hyper_file(days_to_delete, date_column)
        hs.insert_hyper_records()

if __name__ == '__main__':
    gs = GCSFuse('hyper-suite-cr4', './gcs')
    print(gs.mount())