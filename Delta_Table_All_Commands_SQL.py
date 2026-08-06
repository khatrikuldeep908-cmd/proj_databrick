# Databricks notebook source
# DBTITLE 1,Introduction
# MAGIC %md
# MAGIC # Databricks Delta Table Hands-on Notebook (SQL Version)
# MAGIC
# MAGIC This executable notebook demonstrates commonly used Delta table commands in Databricks Unity Catalog using **pure SQL**.
# MAGIC
# MAGIC **Target location**
# MAGIC
# MAGIC - Catalog: `boadbwork`
# MAGIC - Schema: `default`
# MAGIC - Table: `orders_delta_constraints_lc`
# MAGIC
# MAGIC **Included operations**
# MAGIC
# MAGIC 1. Catalog/schema setup
# MAGIC 2. Delta table creation with constraints
# MAGIC 3. Insert records
# MAGIC 4. Describe table extended/detail
# MAGIC 5. Delta history
# MAGIC 6. Add new records
# MAGIC 7. Update records
# MAGIC 8. Delete records
# MAGIC 9. History after DML
# MAGIC 10. Time travel examples
# MAGIC 11. Constraint validation demo
# MAGIC 12. VACUUM dry run and safe VACUUM
# MAGIC 13. OPTIMIZE
# MAGIC 14. Liquid clustering using `CLUSTER BY`
# MAGIC 15. Change clustering keys and run `OPTIMIZE FULL` where supported
# MAGIC 16. Optional cleanup commands
# MAGIC
# MAGIC > Run this notebook on a Databricks cluster or SQL warehouse with Unity Catalog access and privileges on `boadbwork.default`.

# COMMAND ----------

# DBTITLE 1,1. Select catalog and schema
# MAGIC %md
# MAGIC ## 1. Select catalog and schema
# MAGIC
# MAGIC The notebook uses `CREATE CATALOG IF NOT EXISTS` and `CREATE SCHEMA IF NOT EXISTS`. If your user does not have privileges to create catalog/schema, ask the Databricks admin to create `boadbwork.default` first, then rerun from the `USE CATALOG` command onward.

# COMMAND ----------

# DBTITLE 1,Create and use catalog/schema
# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS boadbwork;
# MAGIC USE CATALOG boadbwork;
# MAGIC CREATE SCHEMA IF NOT EXISTS default;
# MAGIC USE SCHEMA default;
# MAGIC SELECT current_catalog() AS current_catalog, current_schema() AS current_schema;

# COMMAND ----------

# DBTITLE 1,2. Drop and create Delta table
# MAGIC %md
# MAGIC ## 2. Drop and create a managed Delta table with constraints and liquid clustering
# MAGIC
# MAGIC This cell makes the notebook rerunnable by dropping the demo table first.
# MAGIC
# MAGIC Constraints used:
# MAGIC
# MAGIC - `order_id BIGINT NOT NULL`
# MAGIC - `customer_id BIGINT NOT NULL`
# MAGIC - Check constraint: `amount >= 0`
# MAGIC - Check constraint: `order_type IN ('ONLINE','STORE','PARTNER')`
# MAGIC - Check constraint: `status IN ('NEW','PROCESSING','COMPLETED','CANCELLED','RETURNED')`
# MAGIC
# MAGIC Liquid clustering is enabled at creation by using `CLUSTER BY (order_date, customer_id)`.

# COMMAND ----------

# DBTITLE 1,Drop and create table
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS boadbwork.default.orders_delta_constraints_lc;
# MAGIC
# MAGIC CREATE TABLE boadbwork.default.orders_delta_constraints_lc (
# MAGIC     order_id BIGINT NOT NULL,
# MAGIC     customer_id BIGINT NOT NULL,
# MAGIC     order_date DATE,
# MAGIC     order_type STRING,
# MAGIC     status STRING,
# MAGIC     amount DECIMAL(10,2),
# MAGIC     country STRING,
# MAGIC     updated_at TIMESTAMP,
# MAGIC     CONSTRAINT amount_positive CHECK (amount >= 0),
# MAGIC     CONSTRAINT valid_order_type CHECK (order_type IN ('ONLINE','STORE','PARTNER')),
# MAGIC     CONSTRAINT valid_status CHECK (status IN ('NEW','PROCESSING','COMPLETED','CANCELLED','RETURNED'))
# MAGIC )
# MAGIC USING DELTA
# MAGIC CLUSTER BY (order_date, customer_id)
# MAGIC TBLPROPERTIES (
# MAGIC     'delta.autoOptimize.optimizeWrite' = 'true',
# MAGIC     'delta.autoOptimize.autoCompact' = 'true',
# MAGIC     'delta.enableChangeDataFeed' = 'true',
# MAGIC     'comment' = 'Demo Delta table with constraints, history, vacuum, optimize, and liquid clustering'
# MAGIC );

# COMMAND ----------

# DBTITLE 1,3. Insert initial records
# MAGIC %md
# MAGIC ## 3. Insert initial records

# COMMAND ----------

# DBTITLE 1,Insert initial records
# MAGIC %sql
# MAGIC INSERT INTO boadbwork.default.orders_delta_constraints_lc
# MAGIC (order_id, customer_id, order_date, order_type, status, amount, country, updated_at)
# MAGIC VALUES
# MAGIC (1001, 501, DATE '2026-08-01', 'ONLINE',  'NEW',        2500.00, 'India', current_timestamp()),
# MAGIC (1002, 502, DATE '2026-08-01', 'STORE',   'COMPLETED',  1800.00, 'India', current_timestamp()),
# MAGIC (1003, 503, DATE '2026-08-02', 'PARTNER', 'PROCESSING', 3200.00, 'UAE',   current_timestamp()),
# MAGIC (1004, 504, DATE '2026-08-03', 'ONLINE',  'COMPLETED',   999.00, 'India', current_timestamp()),
# MAGIC (1005, 505, DATE '2026-08-04', 'STORE',   'NEW',        4500.00, 'USA',   current_timestamp());

# COMMAND ----------

# DBTITLE 1,Verify initial data
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,4. Describe table metadata
# MAGIC %md
# MAGIC ## 4. Describe table metadata
# MAGIC
# MAGIC This section uses `DESCRIBE TABLE EXTENDED`, `DESCRIBE DETAIL`, and `SHOW TBLPROPERTIES`.

# COMMAND ----------

# DBTITLE 1,Describe table extended
# MAGIC %sql
# MAGIC DESCRIBE TABLE EXTENDED boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Describe detail
# MAGIC %sql
# MAGIC DESCRIBE DETAIL boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Show table properties
# MAGIC %sql
# MAGIC SHOW TBLPROPERTIES boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,5. Delta history after creation
# MAGIC %md
# MAGIC ## 5. Show Delta history after table creation and initial insert
# MAGIC
# MAGIC In Databricks Delta, the command for table history is `DESCRIBE HISTORY`.

# COMMAND ----------

# DBTITLE 1,Describe history
# MAGIC %sql
# MAGIC DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,6. Add new records
# MAGIC %md
# MAGIC ## 6. Add new records

# COMMAND ----------

# DBTITLE 1,Insert more records
# MAGIC %sql
# MAGIC INSERT INTO boadbwork.default.orders_delta_constraints_lc
# MAGIC (order_id, customer_id, order_date, order_type, status, amount, country, updated_at)
# MAGIC VALUES
# MAGIC (1006, 506, DATE '2026-08-05', 'ONLINE',  'NEW',        7800.00, 'India',     current_timestamp()),
# MAGIC (1007, 507, DATE '2026-08-05', 'PARTNER', 'PROCESSING', 1250.00, 'Singapore', current_timestamp()),
# MAGIC (1008, 508, DATE '2026-08-06', 'STORE',   'COMPLETED',  2100.00, 'India',     current_timestamp());

# COMMAND ----------

# DBTITLE 1,Verify after insert
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,7. Update records
# MAGIC %md
# MAGIC ## 7. Modify records using UPDATE

# COMMAND ----------

# DBTITLE 1,Update records
# MAGIC %sql
# MAGIC UPDATE boadbwork.default.orders_delta_constraints_lc
# MAGIC SET status = 'COMPLETED',
# MAGIC     amount = amount + 100,
# MAGIC     updated_at = current_timestamp()
# MAGIC WHERE order_id IN (1001, 1003);

# COMMAND ----------

# DBTITLE 1,Verify after update
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,8. Delete records
# MAGIC %md
# MAGIC ## 8. Delete records using DELETE

# COMMAND ----------

# DBTITLE 1,Delete records
# MAGIC %sql
# MAGIC DELETE FROM boadbwork.default.orders_delta_constraints_lc
# MAGIC WHERE status = 'NEW'
# MAGIC   AND amount < 5000;

# COMMAND ----------

# DBTITLE 1,Verify after delete
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,9. History after DML
# MAGIC %md
# MAGIC ## 9. Show Delta history again after INSERT, UPDATE, and DELETE

# COMMAND ----------

# DBTITLE 1,History after DML
# MAGIC %sql
# MAGIC DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,10. Time travel
# MAGIC %md
# MAGIC ## 10. Time travel examples
# MAGIC
# MAGIC These examples read previous table versions. Adjust the version numbers based on the executed transaction history in your workspace. The query below reads the version before the most recent commit (version 3 after CREATE, INSERT, INSERT, UPDATE, DELETE).

# COMMAND ----------

# DBTITLE 1,Time travel - version history
# MAGIC %sql
# MAGIC -- View all versions to pick the one you want
# MAGIC SELECT version, timestamp, operation, operationParameters
# MAGIC FROM (DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc)
# MAGIC ORDER BY version;

# COMMAND ----------

# DBTITLE 1,Time travel - read previous version
# MAGIC %sql
# MAGIC -- Read data as of a previous version (adjust number based on your history)
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc VERSION AS OF 3 ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,11. Constraint validation
# MAGIC %md
# MAGIC ## 11. Constraint validation demo
# MAGIC
# MAGIC The following inserts intentionally violate table constraints. They will produce errors demonstrating that constraints are enforced.

# COMMAND ----------

# DBTITLE 1,Violate amount constraint
# MAGIC %sql
# MAGIC -- This will FAIL: negative amount violates amount_positive check constraint
# MAGIC INSERT INTO boadbwork.default.orders_delta_constraints_lc
# MAGIC (order_id, customer_id, order_date, order_type, status, amount, country, updated_at)
# MAGIC VALUES (9991, 900, DATE '2026-08-06', 'ONLINE', 'NEW', -1.00, 'India', current_timestamp());

# COMMAND ----------

# DBTITLE 1,Violate order_type constraint
# MAGIC %sql
# MAGIC -- This will FAIL: invalid order_type violates valid_order_type check constraint
# MAGIC INSERT INTO boadbwork.default.orders_delta_constraints_lc
# MAGIC (order_id, customer_id, order_date, order_type, status, amount, country, updated_at)
# MAGIC VALUES (9992, 901, DATE '2026-08-06', 'MOBILE', 'NEW', 500.00, 'India', current_timestamp());

# COMMAND ----------

# DBTITLE 1,Verify no bad rows inserted
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,12. VACUUM
# MAGIC %md
# MAGIC ## 12. VACUUM commands
# MAGIC
# MAGIC `VACUUM ... DRY RUN` previews files eligible for removal. The safe command below keeps the default 7-day retention window using `RETAIN 168 HOURS`.
# MAGIC
# MAGIC For training only, do not use very low retention in production because it can break time travel and active workloads.

# COMMAND ----------

# DBTITLE 1,Vacuum dry run
# MAGIC %sql
# MAGIC VACUUM boadbwork.default.orders_delta_constraints_lc RETAIN 168 HOURS DRY RUN;

# COMMAND ----------

# DBTITLE 1,Vacuum
# MAGIC %sql
# MAGIC VACUUM boadbwork.default.orders_delta_constraints_lc RETAIN 168 HOURS;

# COMMAND ----------

# DBTITLE 1,13. OPTIMIZE
# MAGIC %md
# MAGIC ## 13. OPTIMIZE command
# MAGIC
# MAGIC For liquid clustered Delta tables, running `OPTIMIZE` lets Databricks incrementally cluster data as needed.

# COMMAND ----------

# DBTITLE 1,Optimize table
# MAGIC %sql
# MAGIC OPTIMIZE boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Describe detail after optimize
# MAGIC %sql
# MAGIC DESCRIBE DETAIL boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,History after optimize
# MAGIC %sql
# MAGIC DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,14. Liquid clustering
# MAGIC %md
# MAGIC ## 14. Liquid clustering commands
# MAGIC
# MAGIC This section shows how to inspect and change liquid clustering columns. It changes clustering keys from `(order_date, customer_id)` to `(country, order_type)` and runs `OPTIMIZE FULL` where supported.

# COMMAND ----------

# DBTITLE 1,Inspect clustering - detail
# MAGIC %sql
# MAGIC DESCRIBE DETAIL boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Inspect clustering - properties
# MAGIC %sql
# MAGIC SHOW TBLPROPERTIES boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Change clustering keys
# MAGIC %sql
# MAGIC ALTER TABLE boadbwork.default.orders_delta_constraints_lc CLUSTER BY (country, order_type);

# COMMAND ----------

# DBTITLE 1,Incremental optimize after key change
# MAGIC %sql
# MAGIC OPTIMIZE boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,Full reclustering (newer runtimes)
# MAGIC %sql
# MAGIC -- Full reclustering is supported in newer Databricks Runtime versions
# MAGIC OPTIMIZE boadbwork.default.orders_delta_constraints_lc FULL;

# COMMAND ----------

# DBTITLE 1,Verify after clustering change
# MAGIC %sql
# MAGIC DESCRIBE DETAIL boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,History after clustering
# MAGIC %sql
# MAGIC DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,15. Additional Delta commands
# MAGIC %md
# MAGIC ## 15. Additional common Delta commands
# MAGIC
# MAGIC This section includes useful Delta table operations: analyze statistics, restore, clone syntax reference, and change data feed query.

# COMMAND ----------

# DBTITLE 1,Analyze table statistics
# MAGIC %sql
# MAGIC ANALYZE TABLE boadbwork.default.orders_delta_constraints_lc COMPUTE STATISTICS;

# COMMAND ----------

# DBTITLE 1,Query change data feed
# MAGIC %sql
# MAGIC -- Read Change Data Feed (enabled from table creation)
# MAGIC SELECT *
# MAGIC FROM table_changes('boadbwork.default.orders_delta_constraints_lc', 0)
# MAGIC ORDER BY _commit_version, order_id;

# COMMAND ----------

# DBTITLE 1,Restore and clone reference
# MAGIC %sql
# MAGIC -- RESTORE example (uncomment to execute):
# MAGIC -- RESTORE TABLE boadbwork.default.orders_delta_constraints_lc TO VERSION AS OF 2;
# MAGIC
# MAGIC -- SHALLOW CLONE example (uncomment to execute):
# MAGIC -- CREATE TABLE boadbwork.default.orders_delta_constraints_lc_clone SHALLOW CLONE boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,16. Final verification
# MAGIC %md
# MAGIC ## 16. Final verification query

# COMMAND ----------

# DBTITLE 1,Summary aggregation
# MAGIC %sql
# MAGIC SELECT country, order_type, status, COUNT(*) AS total_orders, SUM(amount) AS total_amount
# MAGIC FROM boadbwork.default.orders_delta_constraints_lc
# MAGIC GROUP BY country, order_type, status
# MAGIC ORDER BY country, order_type, status;

# COMMAND ----------

# DBTITLE 1,Final select all
# MAGIC %sql
# MAGIC SELECT * FROM boadbwork.default.orders_delta_constraints_lc ORDER BY order_id;

# COMMAND ----------

# DBTITLE 1,Final history
# MAGIC %sql
# MAGIC DESCRIBE HISTORY boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# DBTITLE 1,17. Optional cleanup
# MAGIC %md
# MAGIC ## 17. Optional cleanup
# MAGIC
# MAGIC Uncomment the command below only when you want to remove the demo table.

# COMMAND ----------

# DBTITLE 1,Cleanup (commented)
# MAGIC %sql
# MAGIC -- Uncomment to drop the demo table:
# MAGIC -- DROP TABLE IF EXISTS boadbwork.default.orders_delta_constraints_lc;

# COMMAND ----------

# MAGIC %sql
# MAGIC --to deleet file for a specific period
# MAGIC VACUUM your_table_name RETAIN 48 HOURS;
# MAGIC
# MAGIC -- additonal info, auto vaccum will delete old file after a certain write operation, by deafult it does not delete old files
# MAGIC ALTER TABLE your_table_name SET TBLPROPERTIES (delta.autoOptimize.autoVacuum = true);
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query changes starting from a specific table version
# MAGIC SELECT * 
# MAGIC FROM table_changes('catalog_name.schema_name.my_table', 1);
# MAGIC
# MAGIC -- Query changes between a specific timestamp range
# MAGIC SELECT * 
# MAGIC FROM table_changes(
# MAGIC     'catalog_name.schema_name.my_table', 
# MAGIC     '2026-08-01 00:00:00', 
# MAGIC     '2026-08-05 23:59:59'
# MAGIC );
# MAGIC