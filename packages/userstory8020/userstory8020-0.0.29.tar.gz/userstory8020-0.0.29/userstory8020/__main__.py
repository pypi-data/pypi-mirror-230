import argparse
import logging

from .app import (AppException, DataFrameManipulation, file_validation,
                  open_spark_session)

main_logger = logging.getLogger(__name__)


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-sp", "--sparkremoteurl", required=True)
        parser.add_argument("-cli", "--clientsdatasetpath", required=True)
        parser.add_argument("-fin", "--finDetailsdatasetpath", required=True)
        parser.add_argument("-c", "--country", action="append", required=True)
        args = parser.parse_args()
        file_validation(filePath=args.clientsdatasetpath)
        file_validation(filePath=args.finDetailsdatasetpath)

        with open_spark_session(spark_remote_url=args.sparkremoteurl) as spark:
            dfm = DataFrameManipulation()
            dfm.clients = spark.read.csv(args.clientsdatasetpath,
                                         sep=',',
                                         header=True)
            dfm.finDetails = spark.read.csv(args.finDetailsdatasetpath,
                                            sep=',',
                                            header=True)
            dfm.clients.show()
            dfm.finDetails.show()
            dfm.filter_rows(filterConditions={"country": args.country})
            dfm.select_columns(colsList=['email', 'country'],
                               colsMap={"btc_a": "bitcoin_address",
                                        "id": "client_identifier",
                                        "cc_t": "credit_card_type"})
            dfm.clients.show()
            dfm.save_output(outputPath="client_data")
    except AppException as e:
        main_logger.error(e)
    except Exception:
        main_logger.info("Programm completed with an ERROR!")
        main_logger.debug("sdfsdfsdff debug")


if __name__ == "__main__":
    main()
