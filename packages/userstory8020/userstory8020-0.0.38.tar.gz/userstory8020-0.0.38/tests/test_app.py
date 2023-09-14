from csv import DictReader

import pytest
from chispa.schema_comparer import assert_schema_equality
from pyspark.sql.types import StringType, StructField, StructType

from userstory8020.app import DataFrameManipulation


@pytest.fixture
def df_manipulation(spark):
    print("dsfsdf")
    test_filename_client = 'source_data/dataset_one.csv'
    test_filename_findetails = 'source_data/dataset_two.csv'
    dfm = DataFrameManipulation()
    # open file in read mode
    with open(test_filename_client, 'r') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        dfm.clients = spark.createDataFrame(list_of_dict)

    with open(test_filename_findetails, 'r') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        dfm.finDetails = spark.createDataFrame(list_of_dict)
    return dfm


def test_counts(df_manipulation):
    assert df_manipulation.clients.count() == 1000
    assert df_manipulation.finDetails.count() == 1000

    df_manipulation.filter_rows(filterConditions={"country": ["United Kingdom",
                                                              "Netherlands"]})

    assert df_manipulation.clients.count() == 100


def test_df_schema(df_manipulation, spark):

    df_manipulation.select_columns(colsList=['email', 'country'],
                                   colsMap={"btc_a": "bitcoin_address",
                                            "id": "client_identifier",
                                            "cc_t": "credit_card_type"})

    expected_schema = StructType([StructField('client_identifier', StringType()),
                                  StructField('country', StringType()),
                                  StructField('email', StringType()),
                                  StructField('bitcoin_address', StringType()),
                                  StructField('credit_card_type', StringType())])
    result_schema = df_manipulation.clients.schema
    assert_schema_equality(expected_schema, result_schema)
