import pyspark
  
# importing sparksession from 
# pyspark.sql module
from pyspark.sql import SparkSession

from pyspark.sql.types import StringType, StructField

from collections import OrderedDict
from csv import DictReader

StructType([StructField('client_identifier', StringType(), True),
            StructField('email', StringType(), True),
            StructField('country', StringType(), True),
            StructField('bitcoin_address', StringType(), True),
            StructField('credit_card_type', StringType(), True)])



# open file in read mode
#with open("source_data/dataset_one.csv", 'r') as f:
#      for line in DictReader(f):
#            print(line)

SparkSession.createDataFrame()

# creating sparksession and giving 
# an app name
#spark = SparkSession.builder.appName('sparkdf').getOrCreate()
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
  
# list  of college data with  dictionary
data = [OrderedDict([('id', '10'), ('first_name', 'Friedrich'), ('last_name', 'Kreutzer'), ('email', 'fkreutzer9@businessweek.com'), ('country', 'France')]),
OrderedDict([('id', '11'), ('first_name', 'Conn'), ('last_name', 'Claiden'), ('email', 'cclaidena@vimeo.com'), ('country', 'France')])]
  
# creating a dataframe
dataframe = spark.createDataFrame(data)
  
# show data frame
dataframe.show()
"""
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col
from typing import Dict, Union, Optional, List


clients: DataFrame
finDetails: DataFrame


##################################
#spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
spark = SparkSession.builder.master("local").appName("chispa").getOrCreate()
clients = spark.read.csv('C:\\Users\\mykkis\\CapGeminiProjects\\userStory8020\\source_data\\dataset_one.csv', sep=',', header=True).alias("clients")
#finDetails = spark.read.csv('/usr/src/userStory8020/source_data/dataset_two.csv', sep=',', header=True).alias("finDetails")
#clients = clients.join(finDetails, ["id"])
clients.show()
clients.write.mode("overwrite").option("header",True).csv("C:\\Users\\mykkis\\CapGeminiProjects\\userStory8020\\outputcsv")


from csv import DictReader


    # open file in read mode
with open("source_data/dataset_one.csv", 'r') as f:
      dict_reader = DictReader(f)
      list_of_dict = list(dict_reader)
      print(list_of_dict)

clients = spark.createDataFrame([{'student_id': 12, 'name': 'sravan', 'address': 'kakumanu'},
                                 {'student_id': 14, 'name': 'jyothika', 'address': 'tenali'},
                                 {'student_id': 11, 'name': 'deepika', 'address': 'repalle'}])
clients.show()




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