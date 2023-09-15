import unittest
import xmlrunner
from parameterized import parameterized, parameterized_class
from sidraconnector.sdk.metadata.models.builders import *
import sidraconnector.sdk.constants as Constants
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
from test.dsuingestion.tabularingestion.utils import Utils as Utils
from test.utils import Utils as TestUtils
      


class TestValidationStringsBase(TestE2EBase):
  
  def execute_tests_validation_strings(self, source_file : str, source_file_extension : str, destination_path : str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    
    #ARRANGE
    attributes = []
    attribute_builder = AttributeBuilder()
    attribute_load_properties_builder = AttributeLoadPropertiesBuilder()
    attribute_load_properties_name = attribute_load_properties_builder.with_is_nullable(is_nullable).with_max_len(max_lenght).with_need_trim(need_trim).with_treat_empty_as_null(treat_empty_as_null).build()
    attribute_load_properties_code = attribute_load_properties_builder.with_max_len(10).build()
    
    attributes.append(attribute_builder.with_name("Name").with_load_properties(attribute_load_properties_name).with_is_primary_key(False).with_databricks_type("STRING").build())
    attributes.append(attribute_builder.with_name("Code").with_load_properties(attribute_load_properties_code).with_is_primary_key(True).with_databricks_type("STRING").build())
    
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file, source_file_extension, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT, entity_attributes = attributes, null_text = null_text)
    
    #Data table is created
    self.assertTrue(Utils.get_table(self._spark, provider.database_name, entity.table_name.lower()))
    
    #Validation errors table is created
    self.assertTrue(Utils.get_table(self._spark, provider.database_name, f"{entity.table_name.lower()}validationerrors"))
    
    #ACT
    self.execute_tabular_ingestion(destination_path)
    
    #ASSERT
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    validation_errors = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}validationerrors")
    df = self._spark.sql(f"SELECT * FROM {entity.table_name.lower()}")
    validation_errors_df = self._spark.sql(f"SELECT ViolatedConstraints FROM {entity.table_name.lower()}validationerrors ORDER BY ViolatedConstraints DESC")

    validations_error_messages = []
    index = 0
    while index < len(expected_error_description):
      if(validation_errors_df.collect()[index][0] != expected_error_description[index]):
        validations_error_messages.append(f"""[Test_ValidationErrors] FAILED: 
                                              Expected validation error message: {expected_error_description[index]}. Current validation error message: {validation_errors_df.collect()[index][0]}. 
                                              ::: Source file: {source_file}, 
                                                  Destination path: {destination_path}, 
                                                  Is nullable: {is_nullable}, 
                                                  Max lenght: {max_lenght}, 
                                                  Null text: {null_text}, 
                                                  Need trim: {need_trim} """)
      self.assertEqual(validation_errors_df.collect()[index][0], expected_error_description[index])
      index += 1
      
    value = validation_errors.select("rows").collect()
    current_errors = value[0].asDict()["rows"]
 
    if(current_errors, expected_errors):
      validations_error_messages.append(f"""[Test_ValidationErrors] FAILED. Expected validation errors: {expected_errors}. Current validation errors: {current_errors}""") 
 
    self.assertEqual(current_errors, expected_errors)
    self._log_validation_and_data_tables(entity.table_name, validations_error_messages)
    
  def _log_validation_and_data_tables(self, table_name : str, validations_error_messages):
    validation_errors_df = self._spark.sql(f"SELECT * FROM {table_name.lower()}validationerrors")
    data = self._spark.sql(f"SELECT * FROM {table_name.lower()}")
    self._logger.warning(f"[E2E-ValidationErrorsStringsTest] VALIDATION ERRORS")
    self._logger.warning(validation_errors_df.show(20, False))
    self._logger.warning(f" [E2E-ValidationErrorsStringsTest] DATA")
    self._logger.warning(data.show(20, False))
   
    index = 0
    while index < len(validations_error_messages):
      self._logger.warning(f"[E2E-ValidationErrorsStringsTest] Validation error message: {validations_error_messages[index]}")
      index += 1

class TestValidationStringsNotNullable(TestValidationStringsBase):
  @parameterized.expand([
    ("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, None, False, False, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, 'NN', False, False, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """,]),
    ("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, None, True, False, 2, ["""`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, None, False, True, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, 'NN', False, True, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """,]),
    ("files/countries_not_null_string.csv", "csv", "countries_not_null_string.csv", False, 15, None, True, True, 3, ["""`Name_SidraProc` IS NOT NULL, """, """`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	])
  def test_string_not_nullables_read_from_csv(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)

  @parameterized.expand([
    ("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, None, False, False, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, 'NN', False, False, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, None, True, False, 2, ["""`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, 'NN', False, False, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, None, True, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, None, False, False, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, 'NN', False, False, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, None, True, False, 2, ["""`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, None, False, True, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, 'NN', False, True, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsx", "xlsx", "countries_not_null_string.xlsx", False, 15, None, True, True, 3, ["""`Name_SidraProc` IS NOT NULL, """, """`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, 'NN', False, True, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xls", "xls", "countries_not_null_string.xls", False, 15, None, True, True, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, None, False, True, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, 'NN', False, True, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.xlsm", "xlsm", "countries_not_null_string.xlsm", False, 15, None, True, True, 3, ["""`Name_SidraProc` IS NOT NULL, """, """`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ])
  def test_string_not_nullables_read_from_excel(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)

  @parameterized.expand([
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, 'NN', False, False, 2, ["""`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, None, True, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, None, False, True, 2, ["""`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, 'NN', False, True, 3, ["""`Name_SidraProc` IS NOT NULL, """, """`Name_SidraProc` IS NOT NULL, ""","""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_not_null_string.parquet", "parquet", "countries_not_null_string.parquet", False, 15, None, True, True, 3, ["""`Name_SidraProc` IS NOT NULL, ""","""`Name_SidraProc` IS NOT NULL, """, """(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ])
  def test_string_not_nullables_read_from_excel(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)

class TestValidationStringsNullable(TestValidationStringsBase):
  @parameterized.expand([
    ("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, 'NN', False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """,]),
    ("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, None, True, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, 'NN', False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """,]),
    ("files/countries_null_string.csv", "csv", "countries_null_string.csv", True, 15, None, True,  True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ])
  def test_string_nullables_read_from_csv(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)

  @parameterized.expand([
    ("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, 'NN', False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, None, True, False,  1,["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, 'NN', False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, None, True, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, 'NN', False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, None, True, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, 'NN', False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsx", "xlsx", "countries_null_string.xlsx", True, 15, None, True, True,  1,["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, 'NN', False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xls", "xls", "countries_null_string.xls", True, 15, None, True, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, 'NN', False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.xlsm", "xlsm", "countries_null_string.xlsm", True, 15, None, True, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ])
  def test_string_nullables_read_from_excel(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)
  
  @parameterized.expand([
    ("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, None, False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, 'NN', False, False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, None, True,  False, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
	("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, None, False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, 'NN', False, True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ("files/countries_null_string.parquet", "parquet", "countries_null_string.parquet", True, 15, None, True,  True, 1, ["""(`Name_SidraProc` IS NULL OR LENGTH(`Name_SidraProc`) <= 15), """]),
    ])
  def test_string_nullables_read_from_parquet(self, source_file : str, source_file_extension : str, destination_path :str, is_nullable : bool, max_lenght : int, null_text : str, need_trim : bool, treat_empty_as_null : bool, expected_errors : int, expected_error_description):
    self.execute_tests_validation_strings(source_file, source_file_extension, destination_path, is_nullable, max_lenght, null_text, need_trim, treat_empty_as_null, expected_errors, expected_error_description)

class TestValidationErrorsStringsValidationText(TestE2EBase):
  
  @parameterized.expand([
    ('files/countries-validationText.csv', "csv", "`name_SidraProc` LIKE 'Bo_%'", 1),
    ('files/countries-validationText.csv', "csv", "", 0),
    ('files/countries-validationText.csv', "csv", None, 0),
  ])
  def test_should_apply_validation_text_if_exists(self, source_file : str, source_file_extension : str, validation_text :str, expected_errors : int):
    # ARRANGE  
    attributes = []
    load_properties = AttributeLoadPropertiesBuilder().with_validation_text(validation_text).build()
    attributes.append(AttributeBuilder().with_name("Name").with_is_primary_key(False).with_load_properties(load_properties).build())
    attributes.append(AttributeBuilder().with_name("Code").with_is_primary_key(True).build())
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file, source_file_extension, entity_attributes = attributes)

    #ACT
    self.execute_tabular_ingestion(destination_path)
    
    #ASSERT
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    validation_errors = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}validationerrors")
    
    value = validation_errors.select("rows").collect()
    count = value[0].asDict()["rows"]
    self.assertEqual(count, expected_errors)

def run_tests():
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationStringsNotNullable))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationStringsNullable))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationErrorsStringsValidationText))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-ValidationErrorsString_Report')
  result = runner.run(suite)

  # print chart
  TestUtils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0