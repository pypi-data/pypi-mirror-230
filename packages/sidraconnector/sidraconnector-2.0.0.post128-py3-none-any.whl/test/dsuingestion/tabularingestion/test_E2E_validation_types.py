import unittest
import xmlrunner
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
from sidraconnector.sdk.metadata.models.builders import *
import sidraconnector.sdk.constants as Constants
from test.dsuingestion.tabularingestion.utils import Utils as Utils
from test.utils import Utils as TestUtils
from pyspark.sql.types import StructType, StructField, StringType
from parameterized import parameterized, parameterized_class

class TestValidationTypesBase(TestE2EBase):     
  def execute_test(self, databricks_type : str, file_extension : str, destination_path :str, is_nullable : bool = False, treat_empty_as_null : bool = False, null_text = None, max_length : int = None, replaced_text :str = None, replacement_text :str = None, data = None, expected_errors : int = 0):    
    #ARRANGE  
    ####Entity
    suffix = self.get_suffix()
    load_properties = LoadPropertiesBuilder().with_re_create_table_on_deployment(True).with_consolidation_mode(Constants.CONSOLIDATION_MODE_SNAPSHOT).with_null_text(null_text).build()

    reader_options = {"header":True}
    if file_extension == "xls":
      reader_options = {"header":0, "keep_default_na":False} #According to the documentation, the number of the header row is 0-indexed
    reader_properties = ReaderPropertiesBuilder().with_header_lines(1).with_file_format(file_extension).with_reader_options(reader_options).build()
    
    file_name_no_extension = self._fixture._get_file_name_no_extension_from_path(destination_path)
    reg_expr = f"^{file_name_no_extension}_((?<year>\d{{4}})(?<month>\d{{2}})(?<day>\d{{2}}))(?:-(?<hour>\d{{2}})(?<minute>\d{{2}})(?<second>\d{{2}}))?.{file_extension}"
   
    entity_in = EntityBuilder().with_name(f"{file_name_no_extension}_{suffix}").with_table_name(f"{file_name_no_extension}_{suffix}").with_load_properties(load_properties).with_regular_expression(reg_expr).with_reader_properties(reader_properties)
    attributes = []
    attribute_builder = AttributeBuilder()
    attribute_load_properties_builder = AttributeLoadPropertiesBuilder()
    attribute_load_properties = attribute_load_properties_builder.with_is_nullable(is_nullable) \
                                      .with_treat_empty_as_null(treat_empty_as_null).with_max_len(max_length)\
                                      .with_replaced_text(replaced_text).with_replacement_text(replacement_text)\
                                      .build()

    attributes.append(attribute_builder.with_name("value").with_load_properties(attribute_load_properties) \
                            .with_is_primary_key(False).with_databricks_type(databricks_type) \
                            .build())
    
    provider, entity = self._fixture.prepare_metadata(entity_in, attributes)
    #Data table is created
    self.assertTrue(Utils.get_table(self._spark, provider.database_name, entity.table_name.lower()))
   
    #Validation errors table is created
    self.assertTrue(Utils.get_table(self._spark, provider.database_name, f"{entity.table_name.lower()}validationerrors"))
    
    #ACT
    schema = StructType([StructField("value", StringType(), True)])

    full_destination_path = self._fixture.get_full_storage_destination_path(destination_path, entity, provider.provider_name)
    self._fixture._storage_fixture.create_file_from_data_frame(file_extension, schema, data, full_destination_path, reader_options)
    self.execute_tabular_ingestion(full_destination_path)

    #ASSERT
    self._spark.catalog.setCurrentDatabase(provider.database_name) 
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}validationerrors")
    value = result.select("rows").collect()
    validation_errors = value[0].asDict()["rows"]
    self._logger.debug(f"[Test_ValidationErrors] Validation errors {validation_errors}")
    if validation_errors != expected_errors : 
      self._logger.warning(f"[Test_ValidationErrors] FAILED. Expected validation errors: {expected_errors}. Actual validation errors: {validation_errors}")
      self._log_validation_and_data_tables(entity.table_name)

    self.assertEqual(validation_errors, expected_errors)    
    
  def _log_validation_and_data_tables(self, table_name : str):
    validation_errors_df = self._spark.sql(f"SELECT * FROM {table_name.lower()}validationerrors")
    data = self._spark.sql(f"SELECT * FROM {table_name.lower()}")
    self._logger.warning(f"[Test_ValidationErrors] VALIDATION ERRORS")
    self._logger.warning(validation_errors_df.show(20, False))
    self._logger.warning(f"[Test_ValidationErrors] DATA")
    self._logger.warning(data.show(20, False))
   

class TestValidationInt(TestValidationTypesBase):

  @parameterized.expand([
  ("csv empty as null","csv", "test_validation.csv", True, True, None, None, [(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("csv NOT empty as null","csv", "test_validation.csv", True, False, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("csv empty as null and null text","csv", "test_validation.csv", True, True, "NN", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 0),
  ("csv empty as null and null text not in data","csv", "test_validation.csv", True, True, "\\k", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsx empty as null","xlsx", "test_validation.xlsx", True, True, None, None, [(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsx NOT empty as null","xlsx", "test_validation.xlsx", True, False, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsx empty as null and null text","xlsx", "test_validation.xlsx", True, True, "null", None,[(-1,),(0,),(1,),(None,),("",),("null",)], 0),
  ("xlsx empty as null and null text not in data","xlsx", "test_validation.xlsx", True, True, "\\k", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xls empty as null","xls", "test_validation.xls", True, True, None, None, [(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xls NOT empty as null","xls", "test_validation.xls", True, False, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xls empty as null and null text","xls", "test_validation.xls", True, True, "NN", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 0),
  ("xls empty as null and null text not in data","xls", "test_validation.xls", True, True, "\\k", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsm empty as null","xlsm", "test_validation.xlsm", True, True, None, None, [(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsm NOT empty as null","xlsm", "test_validation.xlsm", True, False, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ("xlsm empty as null and null text","xlsm", "test_validation.xlsm", True, True, "NN", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 0),
  ("xlsm empty as null and null text not in data","xlsm", "test_validation.xlsm", True, True, "\\k", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 1),
  ])
  def _test_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("INT", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("empty as null","csv", "test_validation.csv", False, True, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 3),
  ("NOT empty as null","csv", "test_validation.csv", False, False, None, None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 3),
  ("null text","csv", "test_validation.csv", False, False, "NN", None,[(-1,),(0,),(1,),(None,),("",),("NN",)], 3),
  ])
  def _test_not_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("INT", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("max length 3","csv", "test_validation.csv", False, False, "NN", 3,[(-1,),(0,),(1,),(None,),("",),("NN",),(100,),(1000,)], 4),
  ])
  def _test_length(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("INT", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("replace text", "csv", "test_validation.csv", "none","0",[(-1,),(0,),(1,),("none",)], 0),
  ("replace text", "csv", "test_validation.csv", "one","1",[(-1,),(0,),(1,),("one",)], 0),
  ])
  def _test_replace_text(self, _, file_extension : str, destination_path :str, replaced_text :str, replacement_text :str, data, expected_errors : int):
    self.execute_test("INT", file_extension = file_extension, destination_path = destination_path, replaced_text = replaced_text, replacement_text= replacement_text, data = data, expected_errors = expected_errors)
  
  @parameterized.expand([
  ("cast_valid", "csv", "test_validation.csv", [("-1",),("0",),("1",),("0.0",)], 0),
  ("cast_invalid", "csv", "test_validation.csv", [(None,),("null",),("none",),("0.8",)], 4),
  ])
  def test_cast(self, _, file_extension : str, destination_path :str, data, expected_errors : int):
    self.execute_test("INT", file_extension = file_extension, destination_path = destination_path, data = data, expected_errors = expected_errors)

class TestValidationDecimal(TestValidationTypesBase):
  @parameterized.expand([
  ("empty as null","csv", "test_validation.csv", True, True, [(0,),(0.1,),(1.1,),(None,),("",),("NN",)], 1),
  ("NOT empty as null","csv", "test_validation.csv", True, False, [(0,),(0.1,),(1.1,),(None,),("",),("NN",)], 1),
  ])
  def test_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool,  data, expected_errors : int):
    self.execute_test("DECIMAL(10,2)", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("empty as null", "csv", "test_validation.csv", False, True, [(0,),(0.1,),(1.1,),(None,),("",),("NN",)], 3),
  ("NOT empty as null", "csv", "test_validation.csv", False, False, [(0,),(0.1,),(1.1,),(None,),("",),("NN",)], 3),
  ])
  def test_not_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, data, expected_errors : int):
    self.execute_test("DECIMAL(10,2)", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("max length 3", "csv", "test_validation.csv", 3, [(1000,)], 1),
  ])
  def test_length(self, _, file_extension : str, destination_path :str, max_length : int, data, expected_errors : int):
    self.execute_test("DECIMAL(10,2)", file_extension = file_extension, destination_path = destination_path, data = data, max_length = max_length, expected_errors = expected_errors)
  
  @parameterized.expand([
  ("DECIMAL(5,2)", "csv", "test_validation.csv", [(-1,),(0,),(1,),(999.99,),(10.085,)], 0), # It is able to perform the cast
  ("DECIMAL(5,2)", "csv", "test_validation.csv", [(999.999,)], 1) # It is not able to perform the cast
  ])
  def test_precision(self, databricks_type : str, file_extension : str, destination_path :str, data, expected_errors : int):
    self.execute_test(databricks_type, file_extension = file_extension, destination_path = destination_path, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("cast_valid", "DECIMAL(5,2)", "csv",  "test_validation.csv", [("-1",),("0",),("1",),("0.0",),("1.0",),("10.01",),("0.001",)], 0),
  ("cast_invalid", "DECIMAL(5,2)","csv", "test_validation.csv", [(1000.1,),(10001,),(10000.1,), (None,),("null",),("none",)], 6),
  ])
  def test_cast(self, _, databricks_type : str, file_extension : str, destination_path :str, data, expected_errors : int):
    self.execute_test("DECIMAL(5,2)", file_extension = file_extension, destination_path = destination_path, data = data, expected_errors = expected_errors)

class TestValidationBoolean(TestValidationTypesBase):
  @parameterized.expand([
  ("empty as null", "csv", "test_validation.csv", True, True, None, None, [(True,),(1,),(False,),(None,),("",),("NN",)], 1),
  ("NOT empty as null", "csv", "test_validation.csv", True, False, None, None, [(True,),(1,),(False,),(None,),("",),("NN",)], 1),
  ])
  def test_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("BOOLEAN", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("empty as null", "csv", "test_validation.csv", False, True, None, None, [(True,),(1,),(False,),(None,),("",),("NN",)], 3),
  ("NOT empty as null", "csv", "test_validation.csv", False, False, None, None, [(True,),(1,),(False,),(None,),("",),("NN",)], 3),
  ])
  def test_not_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("BOOLEAN", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("max length 3", "csv", "test_validation.csv",  3, [(True,),(1,),(False,),(0,)], 2),
  ])
  def test_length(self, _, file_extension : str, destination_path :str, max_length :int, data, expected_errors : int):
    self.execute_test("BOOLEAN", file_extension = file_extension, destination_path = destination_path, max_length = max_length, data = data, expected_errors = expected_errors)
  
  # Be aware that replaced/replacement text has a max length of 5 in database  
  @parameterized.expand([
  ("replace text", "csv", "test_validation.csv", "ok", "True", [(True,),(1,),(False,),(None,),("ok",),("NN",)], 2),
  ("replace text", "csv", "test_validation.csv", "notOk", "0", [(True,),(1,),(False,),(None,),("notOk",),("NN",)], 2),
  ])
  def test_replace_text(self, _, file_extension : str, destination_path :str, replaced_text :str, replacement_text :str, data, expected_errors : int):
    self.execute_test("BOOLEAN", file_extension = file_extension, destination_path = destination_path, replaced_text=replaced_text, replacement_text= replacement_text, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("cast_valid_values", "csv", "test_validation.csv", [("1",),("0",),(1,),(0,),("True",),("False",),("true",),("false",)], 0),
  ("cast_invalid_values", "csv", "test_validation.csv", [(None,),("null",),("none",),("ok",)], 4),
  ])
  def test_cast(self, _, file_extension : str, destination_path :str, data, expected_errors : int):
    self.execute_test("BOOLEAN", file_extension = file_extension, destination_path = destination_path, data = data, expected_errors = expected_errors)

class TestValidationDate(TestValidationTypesBase):
  # Format valid: 2022-07-01
  # CSV treat empty as null by default
  @parameterized.expand([
  ("empty as null", "csv", "test_validation.csv", True, True, None, None, [("2022-07-01",),(None,),("",),("NN",)], 1), 
  ("NOT empty as null", "csv", "test_validation.csv", True, False, None, None, [("2022-07-01",),(None,),("",),("NN",)], 1),
  ("null text", "csv", "test_validation.csv", True, False, "NN", None, [("2022-07-01",),(None,),("",),("NN",)], 0),
  ])
  def test_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("DATE", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("empty as null", "csv", "test_validation.csv", False, True, None,  None, [("2022-07-01",),(None,),("",),("NN",)], 3),
  ("NOT empty as null", "csv", "test_validation.csv", False, False, None, None, [("2022-07-01",),(None,),("",),("NN",)], 3),
  ("NOT empty as null Null text", "csv", "test_validation.csv", False, False, "NN", None, [("2022-07-01",),(None,),("",),("NN",)], 3),
  ])
  def test_not_nullable(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("DATE", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)
    
  @parameterized.expand([
  ("max length 10", "csv", "test_validation.csv", False, False, None, 10,[("2022-01-01T01:00:00+00:00",),("2022-01-01T01:00:00Z",),("2022-01-01",)], 2)
  ])
  def test_length(self, _, file_extension : str, destination_path :str, is_nullable : bool, treat_empty_as_null : bool, null_text, max_length : int, data, expected_errors : int):
    self.execute_test("DATE", file_extension = file_extension, destination_path = destination_path, is_nullable = is_nullable, treat_empty_as_null = treat_empty_as_null, null_text = null_text, max_length = max_length, data = data, expected_errors = expected_errors)

  @parameterized.expand([
  ("date and time", "csv", "test_validation.csv", [("2022-01-01T01:00:00+00:00",),("2022-01-01T01:00:00Z",),("2022-01-01",)], 0),
  ("date only", "csv", "test_validation.csv", [("not a date",),("01-01-2022",),("01/01/2022",),("2022/07/04",),("20220704",),("1656919568",)], 6),
  ])
  def test_format(self,_,file_extension : str, destination_path :str, data, expected_errors : int):
    self.execute_test("DATE", file_extension = file_extension, destination_path = destination_path, data = data, expected_errors = expected_errors)

def run_tests():
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationInt))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationDecimal))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationBoolean))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestValidationDate))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-ValidationTypes_Report')
  result = runner.run(suite)

  # print chart
  TestUtils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0
