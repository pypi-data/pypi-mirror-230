from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col
from typing import Dict, Union, Optional, List


clients: DataFrame
finDetails: DataFrame


##################################
#spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
spark = SparkSession.builder.appName('Read CSV File into DataFrame').getOrCreate()
clients = spark.read.csv('C:\\Users\\mykkis\\CapGeminiProjects\\userStory8020\\source_data\\dataset_one.csv', sep=',', header=True).alias("clients")
#finDetails = spark.read.csv('/usr/src/userStory8020/source_data/dataset_two.csv', sep=',', header=True).alias("finDetails")
#clients = clients.join(finDetails, ["id"])
clients.show()
clients.write.mode("overwrite").option("header",True).csv("C:\\Users\\mykkis\\CapGeminiProjects\\userStory8020\\outputcsv")

"""


clients = filter_rows(df=clients,
                      filterConditions={"country": ["United Kingdom",
                                                    "Netherlands"]})
clients.show()


clients = select_columns(df=clients,
                         colsList=['email', 'country'],
                         colsMap={"btc_a": "bitcoin_address",
                                  "id": "client_identifier",
                                  "cc_t": "credit_card_type"})
clients.show()




finDetails = spark.read.csv('/usr/src/userStory8020/source_data/dataset_two.csv', sep=',', header=True).alias("finDetails")
clients.show()
finDetails.show()

#clients = clients.where(clients.country.isin("United Kingdom", "Netherlands"))
#clients.show()
clients = clients.join(finDetails, (clients.id == finDetails.id)) \
                 .select(col("clients.id").alias("id") \
                       , clients.email \
                       , clients.country \
                       , col("finDetails.btc_a").alias("bitcoin_address") \
                       , col("finDetails.cc_t").alias("credit_card_type")) \
                 .where(clients.country.isin("United Kingdom", "Netherlands"))
clients.show()
#clients.write.mode("overwrite").option("header",True).csv("/usr/src/userStory8020/client_data/outputcsv")
"""