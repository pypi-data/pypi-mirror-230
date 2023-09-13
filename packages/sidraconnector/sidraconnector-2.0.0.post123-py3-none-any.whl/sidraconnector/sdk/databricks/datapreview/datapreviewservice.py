import math
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import urllib.parse
from sidraconnector.sdk.databricks.utils import Utils

class DataPreviewService():
  def __init__(self, spark, logger):
    self.databricks_utils = Utils(spark)
    self.spark = spark       
    self.dbutils = self.databricks_utils.get_db_utils()
    self.logger = logger    

  def create_sqlserver_datapreview_table(self, asset_id, max_sample_records, provider_database, entity_table, entity_id):
   
    source_table = '{provider_database}.{entity_table}'.format(provider_database = provider_database, entity_table = entity_table)
    preview_table = '{provider_database}_{entity_table}'.format(provider_database = provider_database, entity_table = entity_table)
    
    self.logger.debug(f"""[DataPreviewService][create_sqlserver_datapreview_table] Creating data preview table: asset_id: {asset_id}, max_sample_records: {max_sample_records}, provider_database:{provider_database}, source_table: {source_table}, preview_table: {preview_table}""")
    
    jdbcUrl = self.dbutils.secrets.get(scope = "jdbc", key = "coreJdbcDbConnectionString")
    pyOdbcConnectionString = self.dbutils.secrets.get(scope = "pyodbc", key = "corePyOdbcConnectionString")
    table_description = self.spark.sql('DESCRIBE {source_table}'.format(source_table=source_table))
    table_columns = self.spark.sql('SHOW COLUMNS IN {source_table}'.format(source_table=source_table)) 
    
    select_fields=list()
    for field in table_columns.rdd.collect():       
        column_description = table_description.filter(table_description.col_name==field.col_name).first()
        if column_description is None:
            self.logger.warning(f"""[DataPreviewService][create_sqlserver_datapreview_table] Mismatch in column information: {field.col_name}""")
            break;
        if column_description.data_type != 'binary':
            select_fields.append('CAST(' + field.col_name + ' AS STRING)')
            
    select_fields=pd.Series(select_fields).drop_duplicates().tolist()
    select_fields_str = ','.join(select_fields)
    chunk_size = math.floor(2100/len(select_fields)) # sql allows up to 2100 parameters in a query
    # Recreate table
    selectQuery='select {select_fields_str} from {source_table} limit 0'.format(select_fields_str=select_fields_str, source_table=source_table)
    params = urllib.parse.quote_plus(pyOdbcConnectionString)
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
    self.spark.sql(selectQuery).toPandas().to_sql(preview_table, schema='DataPreview', con = engine, chunksize=chunk_size, method='multi', index=False, if_exists='replace')   
    pyOdbcConnection = pyodbc.connect(pyOdbcConnectionString)
    setDynamicDataMaskinCommand='exec [DataPreview].[SetDynamicDataMasking] @IdEntity={entity_id}'.format(entity_id=entity_id)
    pyOdbcConnection.execute(setDynamicDataMaskinCommand)
    pyOdbcConnection.commit()
    pyOdbcConnection.close()
    # Add sample of records
    selectQuery='select {select_fields_str} from {source_table} where IdSourceItem = {asset_id} limit {max_sample_records}'.format(select_fields_str=select_fields_str, source_table=source_table, asset_id = asset_id, max_sample_records=max_sample_records)
    self.spark.sql(selectQuery).toPandas().to_sql(preview_table, schema='DataPreview', con = engine, chunksize=chunk_size, method='multi', index=False, if_exists='append')
    # Insert in DataPreviewLoadHistory
    jsonResults = self.spark.sql(selectQuery).toPandas().to_json(orient='split').replace("\'","\\'")   
    selectQuery = 'select \'{entity_id}\' as IdEntity, \'{preview_table}\' as TableName, LoadDate, \'{jsonResults}\' as LoadJson from {source_table} where IdSourceItem = {asset_id} limit 1'.format(jsonResults=jsonResults, asset_id=asset_id, entity_id=entity_id, source_table=source_table, preview_table=preview_table)
    self.spark.sql(selectQuery).toPandas().to_sql('DataPreviewLoadHistory', schema='DataCatalog', con = engine, chunksize=chunk_size, method='multi', index=False, if_exists='append')

