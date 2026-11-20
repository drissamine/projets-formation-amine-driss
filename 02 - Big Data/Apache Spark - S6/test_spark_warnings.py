import os
import sys

# Set HADOOP_HOME environment variable
os.environ['HADOOP_HOME'] = r'C:\Outils\Spark'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + r'\bin;' + os.environ.get('PATH', '')

print(f"HADOOP_HOME set to: {os.environ['HADOOP_HOME']}")
print(f"Checking for winutils.exe...")

from pyspark import SparkContext, SparkConf

print("\nInitializing Spark...")
conf = SparkConf().setAppName("TestWinutils").setMaster("local[*]")
sc = SparkContext(conf=conf)

print("Spark initialized successfully!")
print(f"Spark Version: {sc.version}")

# Test a simple operation
data = [1, 2, 3, 4, 5]
rdd = sc.parallelize(data)
result = rdd.sum()
print(f"\nTest calculation: sum of {data} = {result}")

sc.stop()
print("\nSpark stopped. Check if the winutils warnings are gone!")
