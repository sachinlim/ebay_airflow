# Airflow Pipeline for eBay Data Extraction

Price Data is gathered from eBay using a Python web scraper called Beautiful Soup, transformed to remove outliers, and averages of the data are loaded onto a Postgres database. The goal of this project is to get a snapshot for the value of used graphics cards (GPUs) today, and at some point in the future, compare how the prices have been fluctuating and how they compare to newer GPUs. 

This entire process is hosted on the cloud through the use of an AWS EC2 instance and AWS RDS for the Postgres database. It runs fully independently on the cloud to automate the process of data extraction, transformation, and loading, every day so that a price history for the Nvidia GPUs can be collected. 

Once enough data has been collected and stored, it can start to give a picture on the price performance of used graphics cards in the (UK) market, especially after the crypto mining boom and crash during and after the COVID-19 pandemic.

### Pipeline Diagram

![image](https://user-images.githubusercontent.com/80691974/218210522-87d52c4a-f802-4898-b8d4-864464363317.png)

### DAG View

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/218771217-fc2a1fb3-d143-430f-bc54-4509d14cca78.png" width="450">
</p>

![image](https://user-images.githubusercontent.com/80691974/218771042-4613259b-3c3e-4551-8488-fdeb22672b5d.png)

### AWS Implementation

The entire process runs off AWS and uses AWS EC2 to host Airflow to run the pipeline, and AWS RDS to use the Postgres database. [This video](https://www.youtube.com/watch?v=o88LNQDH2uI) gives a tutorial on how to set up Airflow on an EC2 instance. It was previously possible to run Airflow on the t2.micro (free) instance, as there were a few articles online about it, but it does not seem to be the case anymore. The video tutorial recommends the use of the t2.small instance, but for this project, the Airflow webpage would crash, leading me to move over to t2.medium instance to run the pipeline. 

This process of hosting the entire process on the cloud was a great way to learn about AWS and see its capabilities. The pipeline and the ETL process is hosted on a single EC2 instance, and for the future, it would be better to host the scripts to other instances/containers to reduce the workload on the Airflow EC2 instance. 

### Nvidia Graphics Cards on eBay

Nvidia and AMD (more recently Intel) GPUs have been sold on eBay for a very long time. During the COVID-19 pandemic, GPUs were being resold at inflated prices due to supply shortages and the crypto mining boom. For example, the RTX 3080 Founders Edition was sold for £649 (RRP) on [Scan](https://www.scan.co.uk) (Nvidia partner) and could be found selling on eBay at £1000+, some were selling beyond £1500 as well. Both new and used GPUs were affected by the price inflation. 

Now, over the past year, GPU prices have fallen, and newer RTX 4000 GPUs are very high in RRP. There have been [videos](https://www.youtube.com/watch?v=9kiOLC2Ca_I) talking about best value GPUs over the past few years, and now, Nvidia GPUs offer better price to performance ratios than before, and the AMD lineups offering even better value. 

For used RTX 3000 GPUs, the prices have fallen below RRP as expected, and people can now get good deals. However, I wanted to track how the prices have fallen and there's no way to do that for used items because it is a fluctuating market where it is mostly private sellers being involved. 

![image](https://user-images.githubusercontent.com/80691974/218760233-e7de148a-2c41-4a80-89f0-b4834d33fbd0.png)


## Data Extraction 

The first phase to extract data focuses on getting all of the price data on eBay. Using the [eBay Advanced Search](https://www.ebay.co.uk/sch/ebayadvsearch) (EAS) feature, it is possible to see sold listings and get an idea on the market value. eBay indicates the sold prices in green, below, with the filters of these items being used and UK only. 

![image](https://user-images.githubusercontent.com/80691974/218758566-f85ac308-2fe8-433d-b7ac-f53c7db34fa5.png)

Using Beautiful Soup and providing the URL to the link obtained by the EAS, it is possible to change a few things from the URL to make sure that the same search filters are applied to all searches, and also to change the search to any item on eBay. For items with spaces, a `+` is used in place before it is added onto the URL - this process can be seen on [this line](https://github.com/sachinlim/ebay_airflow/blob/2527c700d015d3de1c0501e66952c0d43a9947dd/dags/scripts/ebay_extract_price.py#L8) of code.

Once Beautiful Soup is on the correct webpage, it extracts all of the prices (green number in screenshot above) from the search and adds it onto a list, as the size of the list is mostly going to be up to 60 items because only the first page is extracted. Going beyond the first page would add in older sets of data, as the EAS shows sold listing from most recent to oldest, and may add in more outliers.

The delivery cost is not factored in, as this can vary depending on what the courier charges, what the seller wants, or what the seller thinks it may cost. The Nvidia RRP also does not factor in delivery costs, so it is reasonable to exclude delivery costs for this instance. 


## Data Transformation

Once the data has been extracted from EAS, it can be used to calculate the average. It's simple to get the average, but after discovering how EAS worked and how sellers could list (multiple quantities of items in a single listing), certain steps had to be done to get reliable data. The GPU could also be part of a bundle or an entire PC build, resulting in the prices being 2-3 times higher for the entire PC, which is not something we want for this project.


The most important process is to remove outliers, and to do this, 30% of the overall results are [trimmed](https://www.investopedia.com/terms/t/trimmed_mean.asp) (removed). The list is first sorted from lowest to highest, and 15% of the lowest and highest values are removed - trimming from both ends. This results in the reduction of results down to 70% and gives a good number of results to gather the average from, while also removing inflated prices. 


## Data Storage

Now that the price averages have been calculated, this average is saved on a Postgres database. Using Airflow, it dynamically runs the extraction and transformation process for 9 of the RTX 3000 GPUs, and pools all of the results to generate an SQL `INSERT` statement. This SQL statement is then used to insert values into Postgres, with `datetime.now()` being used to generate the primary key as today's date. 

One thing to note about `datetime.now()` is that it is [generally advised](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#creating-a-task) to not use this, as when backtracking the DAGs for previous dates, it will output today's date and not for the instance of the DAG run. This is generally not something that is wanted, but as this project runs once and needs to gather the current day's (date's) averages, it is fine to use. The DAG for this project should never be run for previous dates using `catchup` because it is not possible to calculate price averages for yesterday's results - going back in time is impossible.

![image](https://user-images.githubusercontent.com/80691974/218828686-fc170604-2dee-46c8-8ab2-00c6bfa56d4f.png)

Now that the data is stored on Postgres, it is possible to see how the data has been fluctuating over time. 


## Future (Data) Analysis

Enough data is first needed because this pipeline collects data with a batch processing model, every day at midnight. As of February 14 2023, there are only 6 days worth of data, giving the following result on Google Looker Studio:

![image](https://user-images.githubusercontent.com/80691974/218826603-91c33d95-eaff-4743-b9eb-d4dc92b841bc.png)
Link: https://lookerstudio.google.com/reporting/47f510fa-6d05-4839-a984-9c3f9f790bab/page/tDaFD

It is pretty much a flat line right now, as there is not a lot of price movements. However, looking back on a monthly/weekly scale with 12-24 months worth of data, it would paint a very interesting picture.

