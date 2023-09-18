# logger-local-python-package

# Initialize
run this command in the root directory of your project :

    pip install -r requirements.txt

# Import 
import instance from the package : 

from logger_local.Logger import Logger

# Usage
Note that you must have a .env file with the environment name and logz.io token.
ENVIRONMENT_NAME=...
LOGZIO_TOKEN=...

Logger 1st parameter should be string, appose to object which are structured fields we want to sent to the logger record.
## first initlize
obj={
    'component_id':YOUR_COMPONENT_ID,
    'component_name':YOUR_COMPONENT_NAME,
    'component_category':YOUR_COMPONENT_CATEGORY,
    "developer_email":YOUR_CIRCLES_EMAIL
}
logger=Logger.create_logger()

## local_logger.init()
Please change XXX_ to your component name
Please change yyy to the number of the component you got from your mentor/Team Lead<br>
Please use the CONST enum from logger_local\LoggerComponentEnum.py<br>

```
LOCATION_PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 167
COMPONENT_NAME = 'location-profile-local-python-package/src/location_profile.py'

logger_code_init = {
    'component_id': LOCATION_PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code,
    'developer_email': 'xxx.y@circ.zone'
}
GET_LOCATION_ID_BY_PROFILE_FUNCTION/METHOD_NAME = "get_location_by_bu_profile_id"

local_logger.init(GET_LOCATION_ID_BY_PROFILE_METHOD/FUNCTION, object=logger_code_init)
local_logger.start(GET_LOCATION_ID_BY_PROFILE_ID_METHOD/FUNCTION_NAME, object={'profile_id': profile_id})

local_logger.start(GET_LOCATION_ID_BY_PROFILE_METHOD/FUNCTION_NAME, all parameters )
local_logger.debug(...)
local_logger.info(...)
local_logger.error(...)
local_logger.critical(...)
local_logger.exception(" ...." , ex)
# Send to logger.end all the return values / results
local_logger.end(GET_LOCATION_ID_BY_PROFILE_METHOD/FUNCTION_NAME, object={'location_id':location_id} )
```

### In case of Tests (i.e. Unit-Tests)<br>
Please add logger.init(), logger.error() and logger.critical() to the Tests with all the the fields bellow so we can monitor failing tests from centeral location.<br>
<br>
This is an example, please use the right values<br>
```
COMPONENT_NAME = 'location-profile-local-python-package/tests/test_location_profile.py'
object_unit_test_init = {
    'component_id': LOCATION_PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': COMPONENT_NAME,
    'component_category':LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework':LoggerComponentEnum.testingFramework.Python_Unittest.value
    'developer_email': 'xxx.y@circ.zone'
}
```
#### In each method<br>
```
GET_LOCATION_ID_BY_PROFILE_TEST_METHOD/FUNCTION_NAME = "get_location_id_test"
local_logger.start(GET_LOCATION_ID_BY_PROFILE_TEST_METHOD/FUNCTION_NAME, all parameters )
local_logger.debug(...)
local_logger.info(...)
local_logger.error(...)
local_logger.critical(...)
local_logger.exception(" ...." , ex)
local_logger.end(TEST_GET_LOCATION_ID_BY_PROFILE_FUNCTION_NAME, return value / result )
```
## logcal_loger.start()
// Send the logger all the parameter of method/function<br>
```
def func( aaa, bbb):
logger.start("Hi", {
    'aaa':aaa,
    'bbb': bbb
})
```
## Others
You can add any field value you want to any of the methods<br?
```
logger.info("Hi", {
    'xxx': xxx_value,
    'yyy': yyy_value
})
```
## local_logger.end()
The general structure of logger.end() calls
```
result = .....
logger.end("....", { 'result': result })
return result
```
you can insert log into DB with 2 difference approach :<br>

1. Writing a message :<br>
    * local_logger.info("your-message");<br>
    * local_logger.error("your-message");<br>
    * local_logger.warn("your-message");<br>
    * local_logger.debug("your-message");<br>
    * local_logger.verbose("your-message");<br>
    * local_logger.start("your-message");<br>
    * local_logger.end("your-message");<br>
    * local_logger.Init("your-message");<br>
    * local_logger.exception("your-message");<br>

2. Writing an object (Dictionary) :
    
   In case you have more properties to insert into the database,
   
   you can create a Dictionary object that contains the appropriate fields from the table and send it as a parameter.
   You can use local_logger.init if you want to save the fields for a few logging action. at the end please use clean_variables() function to clear those fields

   the Dictionary's keys should be the same as the table's columns names and the values should be with the same type as the table's columns types.

        objectToInsert = {
            'user_id': 1,
            'profile_id': 1,
            'activity': 'logged in the system',
            'payload': 'your-message',
        }

        local_logger.info(object=objectToInsert);
    
    None of the fields are mandatory.

3. Writing both object and message:
just use both former aproaches together as you can watch in here:
local_logger.info("your-message",object=objectToInsert);


Please add to requirements.txt<br>
replace the x with the latest version in pypi.org/project/logger-local<br>
logger-local==0.0.x <br>
<br>
Please include at least two Logger calls in each method:<br>
object1={
    arg1: arg1_value
    arg2: arg2_value
}
local_logger.start(object=object1)
object2={
    return: ret_value
}
local_logger.end(object=object2)

if you catch any exceptions please use:
exception exception as ex
local_logger.exception(object=e)

TOOD: We nee to add Unit Tests so this command will work<br>
python -m unittest .\tests\test_writer.py<br>


pip install -r .\requirements.txt<br>

To Run the tests (Not Unit Tests)<br>
python.exe .\tests\test_writer.py<br>
