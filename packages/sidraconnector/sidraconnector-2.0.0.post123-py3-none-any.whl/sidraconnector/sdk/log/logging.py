from sidraconnector.sdk.databricks.utils import Utils
from applicationinsights import TelemetryClient # To be replaced by opencensus
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.log_exporter import AzureEventHandler
import sys


class Logger():
    def __init__(self, spark):
        self.spark = spark
        self.databricks_utils = Utils(spark)

    def create_telemetry_logger(self):
        instrumentation_key = self.databricks_utils.get_databricks_secret('log', 'ApplicationInsights--InstrumentationKey')
        logger = TelemetryClient(instrumentation_key)
        return logger
    
     # You can send customEvent telemetry in exactly the same way that you send trace telemetry except by using AzureEventHandler instead.
    
    def create_logger(self, name, use_azure_log = False, use_custom_events = False):
        instrumentation_key = self.databricks_utils.get_databricks_secret(scope='log', key='ApplicationInsights--InstrumentationKey')
        logger = logging.getLogger(name)
        
        streamHandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        
        logger.addHandler(streamHandler)  
        if use_azure_log is True:
            logger.addHandler(AzureLogHandler(connection_string=f"InstrumentationKey={instrumentation_key}"))
        # Custom events is not working as expected
        if use_custom_events is True:
            logger.addHandler(AzureEventHandler(connection_string=f"InstrumentationKey={instrumentation_key}"))
        return logger
    
    # OpenCensus -> after flush do a delay of 20 seconds to ensure write the info                    
    # After create the logger stablish a different level if needed. By default it is Warning. 
    # logger.setLevel(logging.DEBUG)