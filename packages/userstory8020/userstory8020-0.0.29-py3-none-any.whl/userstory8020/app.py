import logging
from contextlib import contextmanager
from csv import Error, Sniffer
from os import R_OK, access
from pathlib import Path
from typing import Dict, List, Optional, Union

from pyspark.sql import SparkSession
from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.functions import col

app_logger = logging.getLogger(__name__)


@contextmanager
def open_spark_session(spark_remote_url: str):
    spark_session = SparkSession.builder \
                                .remote(spark_remote_url) \
                                .getOrCreate()
    try:
        app_logger.debug("Spark session is opened.")
        yield spark_session
    finally:
        spark_session.stop()
        app_logger.debug("Spark session is closed.")


class DataFrameManipulation:
    def __init__(self) -> None:
        self.__clients: DataFrame
        self.__finDetails: DataFrame

    @property
    def clients(self) -> DataFrame:
        return self.__clients

    @clients.setter
    def clients(self, df: DataFrame) -> None:
        if isinstance(df, DataFrame):
            self.__clients = df

    @property
    def finDetails(self):
        return self.__finDetails

    @finDetails.setter
    def finDetails(self, df: DataFrame) -> None:
        if isinstance(df, DataFrame):
            self.__finDetails = df

    def filter_rows(self,
                    filterConditions: Dict[str,
                                           Union[str,
                                                 List[str]]]) -> None:
        logging.info('Filtering data.')
        logging.debug(f'filterConditions - {filterConditions}')
        for col_name, col_value in filterConditions.items():
            self.clients = self.clients \
                               .filter(self.clients[col_name].isin(col_value))
        logging.info('Data is filtered.')

    def select_columns(self,
                       colsList: List[str],
                       colsMap: Optional[Dict[str, str]] = None) -> None:
        logging.info('Selecting columns.')
        logging.debug(f'colsList - {colsList}')
        self.clients = self.clients.join(self.finDetails, ["id"])
        if colsMap:
            self.rename_columns(colsMap=colsMap)
            colsList.extend(colsMap.values())
        self.clients = self.clients.select([c for c in self.clients.columns if c in colsList])
        logging.info('Columns selected.')

    def rename_columns(self,
                       colsMap: Dict[str, str]) -> None:
        logging.info('Renaming columns.')
        logging.debug(f'colsMap - {colsMap}')
        self.clients = self.clients.select([col(c).alias(colsMap.get(c, c)) for c in self.clients.columns])
        logging.info('Columns renamed.')

    def save_output(self, outputPath: str):
        logging.info('Saving output.')
        logging.debug(f'OutputPath - {outputPath}')
        self.clients.write \
                    .mode("overwrite") \
                    .option("header", True) \
                    .csv(outputPath)
        logging.info('Output saved.')


def file_validation(filePath: str) -> None:
    p = Path(filePath)
    if p.exists() and p.is_file():
        if access(filePath, R_OK):
            try:
                with open(filePath, newline='') as csvfile:
                    start = csvfile.read(1024)
                    Sniffer().sniff(start)
                    if not Sniffer().has_header(start):
                        app_logger.error("Seems to be the header is absent.")
                        raise AppException(f'file: {filePath} is incorrect!')
            except Error as e:
                app_logger.error(e)
                raise AppException(f'file: {filePath} is incorrect!') from e
        else:
            err_msg = 'No sufficient access to the file.'
            app_logger.error(err_msg)
            raise AppException(err_msg)
    else:
        err_msg = 'The file or directory does not exist!'
        app_logger.error(err_msg)
        raise AppException(err_msg)


class AppException(Exception):
    pass
