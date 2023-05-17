import argparse
import pyspark
from pyspark.sql import types
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

def init_spark():
    spark = SparkSession.builder \
        .appName('Project DE 2023') \
        .getOrCreate()
    spark.conf.set("temporaryGcsBucket", "dataproc-temp-us-central1-761219073036-0scxgvoy")
    return spark

def clean_inventory_data(spark, df):
    """ Data clearning example """

    print(f"Pre: {df.count()} rows")
    df.createOrReplaceTempView('inventory_sets')

    print("Remove Null inventory id")
    df = spark.sql("""
        SELECT 
            *
        FROM 
            inventory_sets
        WHERE 1=1
            AND inventory_id IS NOT NULL
    """
    )

    print(f"Post: {df.count()} rows")
    return df

def clean_set_data(spark, df):
    """ Data clearning example """

    print(f"Pre: {df.count()} rows")
    df.printSchema()

    df.createOrReplaceTempView('set')

    print("Remove non-valid year...")
    df = spark.sql("""
        SELECT 
            *
        FROM 
            set
        WHERE 1=1
            AND (name IS NOT NULL
                OR year IS NOT NULL
                OR theme_id IS NOT NULL
                OR num_parts IS NOT NULL
                OR img_url IS NOT NULL
            )
    """
    )

    # df.show(5)
    # only use yyyyMMdd
    df = df.withColumn("year", F.col("year").cast("string")) \
        .withColumn("year", F.to_date(F.concat(F.col("year"), F.lit('0101')), "yyyyMMdd")) \
        .filter((F.col("year") >= "1932-01-01") & (F.col("year") <= "2024-01-01"))

    df.show(5)
    print(f"Post: {df.count()} rows")
    return df


def aggregate_data(spark, df_0, df_1, df_2):
    df_0.createOrReplaceTempView('inventory_sets')
    df_1.createOrReplaceTempView('set')
    df_2.createOrReplaceTempView('themes')

    df_result_0 = spark.sql("""
        SELECT 
            inventory_id,
            ivs.set_num,
            quantity,
            s.name AS set_name,
            s.year,
            theme_id,
            t.name AS theme_name,
            num_parts,
            img_url
        FROM
            inventory_sets AS ivs
            LEFT JOIN (
                SELECT 
                    *
                FROM 
                    set
            ) AS s ON s.set_num = ivs.set_num
            LEFT JOIN (
                SELECT 
                    *
                FROM 
                    themes
            ) AS t ON t.id = s.theme_id
        """
    )

    df_result_1 = df_1 \
        .groupBy("year").count()

    df_result_0.printSchema()
    df_result_1.printSchema()
    return df_result_0, df_result_1


def load_data_from_BQ(spark, table_name):
    df = spark.read.format('bigquery') \
        .option('table', f'vande2023.vande2023.{table_name}') \
        .load()

    df.printSchema()
    return df


def write_to_BQ(df, table_name):
    print(f"Write df to table vande2023.{table_name} in BiqQuery with schema:")
    df.printSchema()
    df.show(5)
    # We can set append mode as batch processing
    if "year" in df.columns and "theme_id" in df.columns:
        df.write.format('bigquery') \
            .option('partitionField', "year")\
            .option('partitionType', 'DAY')\
            .option("clusteredFields", "theme_id") \
            .option("overwriteSchema", "True") \
            .option('table', f"vande2023.{table_name}") \
            .mode('overwrite') \
            .save()
    elif "year" in df.columns and "theme_id" not in df.columns:
        df.write.format('bigquery') \
            .option('partitionField', "year")\
            .option('partitionType', 'DAY') \
            .option("overwriteSchema", "True") \
            .option('table', f"vande2023.{table_name}") \
            .mode('overwrite') \
            .save()
    else:
        df.write.format('bigquery') \
            .option("overwriteSchema", "True") \
            .option('table', f"vande2023.{table_name}") \
            .mode('overwrite') \
            .save()


def main_spark_job(table_names):
    table_is = table_names[0] # inventory_sets
    table_s = table_names[1] # sets
    table_t = table_names[2] # themes
    
    spark = init_spark()

    df_is = load_data_from_BQ(spark, table_is)
    df_s = load_data_from_BQ(spark, table_s)
    df_t = load_data_from_BQ(spark, table_t)

    clean_df_is = clean_inventory_data(spark, df_is)
    clean_df_s = clean_set_data(spark, df_s)
    df_result_0, df_result_1 = aggregate_data(spark, clean_df_is, clean_df_s, df_t)
    
    write_to_BQ(df_result_0, "clean_lego_data_0")
    write_to_BQ(df_result_1, "clean_lego_data_1")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_0', required=True)
    parser.add_argument('--input_1', required=True)
    parser.add_argument('--input_2', required=True)

    args = parser.parse_args()

    main_spark_job([args.input_0, args.input_1, args.input_2])
