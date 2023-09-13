import sys
from sidraconnector.sdk import constants
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.storage.utils import Utils
from sidraconnector.sdk.databricks.dsuingestion.tabularingestionservice import TabularIngestionService
from sidraconnector.sdk.databricks.datapreview.datapreviewservice import DataPreviewService
from sidraconnector.sdk.databricks.reader.readerservice import ReaderService

class TabularIngestion():
    def __init__(self, spark):
        self.spark = spark
        self.utils =  Utils(spark)
        self.logger = Logger(spark, self.__class__.__name__)
        self.reader_service = ReaderService(spark, self.logger)
        self.data_preview_service = DataPreviewService(spark, self.logger)

    def process(self, asset_id : int, asset_uri : str, asset_is_full_extract : bool):
        self.logger.debug(f"[get_tabular_ingestion_service] Asset_Id: {asset_id}, Asset_Uri:{asset_uri}, Asset_Is_Full_Extract: {asset_is_full_extract}")
        self.tabular_service = TabularIngestionService(self.spark, self.logger, asset_uri, asset_id, asset_is_full_extract)
        
        if self.tabular_service.asset_is_registered is False:
            registered_asset = self.tabular_service.register_asset()
            self.logger.debug(f"[TabularIngestion]: Registered asset: {registered_asset}")
            file_name = self.tabular_service.get_wasbs_file(registered_asset.destination_uri)
            self.logger.debug(f"[TabularIngestion]: Copying file: {registered_asset.source_uri} to {file_name}")
            self.tabular_service.copy_raw_file(registered_asset.source_uri, file_name)
            registered_asset_info = self.tabular_service.register_info(registered_asset)
            self.tabular_service.delete_source_file(registered_asset.source_uri)
        else: 
            file_name = self.utils.https_to_wasbs(self.tabular_service.asset_uri)

        self.tabular_service.set_metadata_information()

        file_dataframe = self.reader_service.read_file(file_name, self.tabular_service.entity)
        file_dataframe = self.tabular_service.add_is_deleted_column(file_dataframe)

        if self.tabular_service.get_consolidation_mode() == constants.CONSOLIDATION_MODE_SNAPSHOT:
            self.tabular_service.truncate_old_partition_from_same_file()

        column_names = self.tabular_service.get_non_calculated_field_names()
        self.tabular_service.delete_from_table()

        if file_dataframe.count() > 0:
            file_dataframe = file_dataframe.toDF(*column_names)
            self.tabular_service.create_staging_table(file_dataframe)
            self.tabular_service.configure_query_optimization()
            self.tabular_service.create_table_and_validations_staging_query()
            
            #if tabular_service.has_to_generate_change_data_feed() is True:
                # TODO: Not Implemented yet: It will be changed for Change Data Feed from Databricks
                #tabular_service.insert_data_into_delta_table() 
            #self.logger.debug(f"[TabularIngestion]: Starting ingestion with consolidation mode: {self.tabular_service.get_consolidation_mode()}")
            
            if self.tabular_service.get_consolidation_mode() == constants.CONSOLIDATION_MODE_SNAPSHOT:
                self.tabular_service.insert_snapshot_data_into_final_table()
            elif self.tabular_service.get_consolidation_mode() == constants.CONSOLIDATION_MODE_MERGE:
                self.tabular_service.insert_merge_data_into_final_table() 
            #else: # OVERWRITE MODE, not implemented yet

            self.tabular_service.insert_into_validation_errors_table()

            self.tabular_service.drop_staging_tables()

            # Generate DATA CATALOG
            if self.tabular_service.has_to_generate_data_catalog() is True:
                try: 
                    provider_database = self.tabular_service.get_provider_database()
                    entity = self.tabular_service.get_entity()
                    entity_id = entity.id
                    entity_table = entity.table_name
                    asset_id = self.tabular_service.get_asset_id()

                    self.data_preview_service.create_sqlserver_datapreview_table(asset_id, constants.DATACATALOG_SAMPLE_NUMBER_RECORDS, provider_database, entity_table, entity_id)
                except:
                    self.logger.exception('Error on create_sqlserver_datapreview_table: %s' %sys.exc_info()[1])

        self.tabular_service.finish_loading(file_dataframe.count())  
