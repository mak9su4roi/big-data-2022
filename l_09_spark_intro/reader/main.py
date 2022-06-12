from pyspark.sql import SparkSession
from string import Template
import logging

BLUE = "\x1b[38;5;39m"
tpl = Template("${colour}There are ${num} lines in .csv file (excluding header)\x1b[0m")
ss = SparkSession.builder.appName('l_09').getOrCreate()
logging.error(tpl.substitute(
        colour=BLUE,
        num=ss.read.option('header', 'true').csv('/opt/app/PS_20174392719_1491204439457_log.csv').count()
    )
)