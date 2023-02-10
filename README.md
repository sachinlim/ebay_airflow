# Airflow Pipeline for eBay Data Extraction

Price Data is gathered from eBay using a Python web scraper called Beautiful Soup, transformed to remove outliers, and averages of the data are loaded onto a Postgres database. The goal of this project is to get a snapshot for the value of used graphics cards (GPUs) today, and at some point in the future, compare it to the prices and newer GPUs, then. 

This entire process is hosted on the cloud through the use of an AWS EC2 instance and AWS RDS for the Postgres database. It runs fully independently on the cloud to automate the process of data extraction, transformation, and loading, every day so that a price history for the Nvidia GPUs can be collected. 

Once enough data has been collected and stored, it can start to give a picture on the price performance of used graphics cards in the (UK) market, especially after the crypto mining boom and crash during and after the COVID-19 pandemic.

### Pipeline Diagram

![image](https://user-images.githubusercontent.com/80691974/218210522-87d52c4a-f802-4898-b8d4-864464363317.png)



## Nvidia Graphics Cards on eBay


## Data Extraction 


## Data Transformation


## Data Storage


## Future (Data) Analysis

Enough data is first needed because this pipeline collects data with a batch processing model, every day at midnight.
