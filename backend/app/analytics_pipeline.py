from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg, count, datediff
import sqlite3
import pandas as pd
import os
import json

DB_FILE = "hotel_booking.db"
OUTPUT_REPORT = "backend/app/analytics_report.json"

def run_analytics_pipeline():
    print("=============================================================")
    print("         LUXURY HAVENS PYSPARK ANALYTICS PIPELINE           ")
    print("=============================================================")

    if not os.path.exists(DB_FILE):
        print(f"[!] SQLite DB file '{DB_FILE}' not found. Run seed script or make a booking first.")
        return

    # 1. Initialize SparkSession (running in local mode)
    spark = SparkSession.builder \
        .appName("LuxuryHavensAnalytics") \
        .master("local[*]") \
        .getOrCreate()
        
    print("[✓] Spark Session active.")

    # 2. Extract SQLite tables via pandas and load into Spark DataFrames
    # This prevents JDBC JAR issues and works out-of-the-box in all local runtimes!
    conn = sqlite3.connect(DB_FILE)
    
    print("[✓] Reading database tables...")
    df_bookings_pd = pd.read_sql_query("SELECT id, booking_code, room_id, check_in, check_out, total_price, status, guest_count FROM bookings", conn)
    df_rooms_pd = pd.read_sql_query("SELECT id, hotel_id, room_type, price_per_night FROM rooms", conn)
    df_hotels_pd = pd.read_sql_query("SELECT id, name, city, country, rating FROM hotels", conn)
    
    conn.close()

    if df_bookings_pd.empty:
        print("[!] No bookings found in the database. Seeding data is required.")
        spark.stop()
        return

    # Convert to Spark DataFrames
    bookings_df = spark.createDataFrame(df_bookings_pd)
    rooms_df = spark.createDataFrame(df_rooms_pd)
    hotels_df = spark.createDataFrame(df_hotels_pd)

    # 3. Perform Spark Data Transformations & Aggregations
    print("[✓] Compiling Spark SQL Transformations...")
    
    # Calculate stay duration (nights) inside Spark
    bookings_df = bookings_df.withColumn("nights", datediff(col("check_out"), col("check_in")))

    # Join Bookings with Rooms and Hotels
    # bookings.room_id = rooms.id -> rooms.hotel_id = hotels.id
    joined_df = bookings_df.join(rooms_df, bookings_df.room_id == rooms_df.id) \
                           .join(hotels_df, rooms_df.hotel_id == hotels_df.id)

    # A. Calculate Revenue per City (Confirmed stays only)
    revenue_by_city_df = joined_df.filter(col("status") == "confirmed") \
                                  .groupBy("city") \
                                  .agg(_sum("total_price").alias("total_revenue"), count("id").alias("confirmed_bookings")) \
                                  .orderBy(col("total_revenue").desc())
    
    print("\n--- CONFIRMED REVENUE BY CITY ---")
    revenue_by_city_df.show()

    # B. Calculate Stay Statistics per Room Type
    room_stats_df = joined_df.groupBy("room_type") \
                             .agg(avg("nights").alias("avg_stay_nights"), avg("total_price").alias("avg_spend")) \
                             .orderBy(col("avg_spend").desc())
                             
    print("--- ROOM TYPE STAY STATISTICS ---")
    room_stats_df.show()

    # C. Top Hotels by Total confirmed revenue
    top_hotels_df = joined_df.filter(col("status") == "confirmed") \
                             .groupBy("name", "city") \
                             .agg(_sum("total_price").alias("confirmed_revenue"), avg("rating").alias("rating")) \
                             .orderBy(col("confirmed_revenue").desc())

    print("--- TOP HOTEL DESTINATIONS BY REVENUE ---")
    top_hotels_df.show()

    # 4. Save results to report JSON
    # Collect Spark data back to Python driver to write structured report
    revenue_by_city = [row.asDict() for row in revenue_by_city_df.collect()]
    room_stats = [row.asDict() for row in room_stats_df.collect()]
    top_hotels = [row.asDict() for row in top_hotels_df.collect()]

    report_payload = {
        "generated_at": datetime.now().isoformat(),
        "revenue_by_city": revenue_by_city,
        "room_stats": room_stats,
        "top_hotels": top_hotels
    }

    # Ensure parent folders exist
    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w") as f:
        json.dump(report_payload, f, indent=4)
        
    print(f"[✓] Spark Analytics summary report compiled successfully at: {OUTPUT_REPORT}")
    
    # Terminate Spark Session gracefully
    spark.stop()
    print("=============================================================")

if __name__ == "__main__":
    run_analytics_pipeline()
