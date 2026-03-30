# Assignment 1

## Structure smart_house.py
In this section, the whole structure of the smart_house.py file as well as some of the design decisions are described.

#### Header
We included from typing the keyword callable to assert functions as return types.
We used static values for certain keys (parent, class, classname, new) to reduce mental load and key errors.

#### Functions for interacting with the class
- Function find: Uses recursion to find a given method name in the current and the parent classes (multiple inheritances are possible). It returns the callable with the correct name or raises a NotImplementedError.
- Function call: Calls the provided function name by using find. This is used to assure the correct method calls by the subclasses, if their parent classes only provide abstract classes. 
- Function make: Makes a new instance of the class that is the first argument by calling the new key for executing the right instantiation of the class.

#### Parent class: Device
- Functions get_power_consumption and describe_device: Those are abstract methods. They get executed by the call function and call the corresponding methods of the subclass. If they are called by a device object, they raise a NotImplementedError. 
- Function toggle_status: All subclasses of device can call this method. It checks the current status and toggles from 'on' to 'off' and vice versa. If an unknown status is found, an AttributeError is raised.
- Function new_device: This method is called by the new_function of the subclasses, to inherit the attributes of the parent class. It returns a dictionary with all the attributes a device has. 
- Dictionary device: This dictionary holds all the methods and attributes a device has and is used by instantiating a new object. 

#### Parent class: Connectable
- Functions connect, disconnect and is_connected: Those methods are called by the call function directly and work for all subclasses of connectable the same. If the method connect is used, the attribute connected is set to True and the attribute ip is set to the string provided as argument. The disconnect method sets the attribute connected to False and the is_connected method returns the attribute connected. 
- Function new_connectable: takes two optional arguments for connected and ip. If none if provided, all connectables are set to False (not connected) by default as well as the saved ip is an empty string. It returns a dictionary with the optional arguments and a class dictionary for connectable. 
- Dictionary connectable: Same as for dictionary device with connectable attributes.

#### Subclass: Light
- Function get_power_consumption_light: This is the method for the abstract get_power_consumption by the parent class device for lights. It returns 0.0 if the status is off, it returns the calculated float using base power and brightness.
- Function describe_light: This is the method for the abstract describe_device by the parent class device for lights. It returns a string containing the attributes name, location, status and brightness.
- Function new_light: It calls the make function on the parent class device with the according arguments first, then makes a dictionary with the class key and the brightness and then returns a dictionary by merging the two dictionaries (device and light) by the pipe operator, which merges dictionaries left to right (keys in left dictionary get overwritten by right dictionary). We used this way of merging, because it is simple and displays the inheritance order (highest order parent classes to the left, subclass to the right).
- Dictionary Light: This is a dictionary with all the methods for lights. It has Device in the list at key parent_key, to enable using methods defined in the parent class.

#### Subclass: Thermostat:
- Functions get_power_consumption_thermostat and describe_thermostat: Those methods work in the same way like in the light subclass but with a slightly different calculation for the power consumption and a different string for description. 
- Functions set_target_temperature and get_target_temperature: These change or return the value of the attribute target_temperature.
- Function new_thermostat: This creates a new instance of thermostat by calling the make function first for device then for connectable, since thermostat inherits from both parents. It creates a dictionary for a new thermostat in which the attributes target_temperature and room_temperature are saved. It returns the merged dictionaries with device dictionary to the left, connectable dictionary in the middle and the thermostat dictionary to the right between/of the two pipe operators. (Since the classes device and connectable are independent of each other, the order of device and connectable is irrelevant, the important order is that the subclass dictionary is to the right.)
- Dictionary Thermostat: Holds all the methods for this subclass and the connection to the parent classes by adding both of them in the list for parent_key.

#### Subclass: Camera
This subclass works the same way like the thermostat with the slight difference that no temperatures are saved instead the resolution of the camera is saved. This reduces the methods to the specific methods for devices that need to be defined. The instantiation with the function new_camera as well as the dictionary for the class works the same as for the thermostat.

#### Class: SmartHouseManagement
- Function new_SmartHouseManagement: This function just returns a dictionary with the class key smarthousemanagement. This is used only to use the functions call.
- Function search: This is a helper function to increase readability of the other methods in this class. It returns a dictionary that is derived from globals by filtering out the instances and then removing instances according to the arguments search_type and search_room. 
- Function calculate_total_power_consumption: This function uses the function search first, to assure that result is calculated only for the correct instances. It iterates over the received dictionary, uses the method get power consumption, since this is already implemented and adds the returns up. In the end, it simply returns the added number.
- Function get_all_device_description: This function works the same way as calculate_total_power_consumption but instead of adding a return value, it concatenates the string, that is returned by the method call describe_device for each instance in the filtered dictionary. 
- Function get_all_connected_devices: This method returns a string of device descriptions and power consumptions but only for connected devices. It uses a similar approach like the other functions above. It gathers all instances in a dictionary, that have the class connectable as parent class and then filters that dictionary to all the active and connected instances. While iterating over this filtered dictionary, a string with all device descriptions as well as the power consumption is concatenated and returned in the end.

#### Instances
Only a few instances are shown in this file to have a overview over the whole program. An in-depth and more complete run over all methods is accomplished in the testing file. 


## Tests
In this section the tests of the file `test_smart_house.py` are described. It is structured according to the class functions which are tested.
Generally, we test the function directly with the mocked instantiated object which the function is written for. E.g. For the thermostat, we have our mocked instantiated object via the setup function, and test then directly the function `set_target_temperature` instead of using the `call` function.
We used the library argparse to handle CLI arguments for the tests. 
The helper function run_tests executes all functions starting with test_ .  Before each test execution the setup function is run to instantiate all mock devices used for testing and after each test, the teardown function removes all mock devices. This ensures that the running order of the tests do not play a role in the test outcomes, since for example every toggle of the status can affect these. These instances are created and set as global variables with the function `setup`. This function is called before each test execution, so that we also have the same state and properties of the mock object. This implies also, that we destroy all the mock objects after the test finished with the `teardown` function.

#### Test runner
The function `run_tests` collects all tests available in the file `test_smart_house.py` and executes them. There are three states which each of the tests can have: 

| State      | Description     |
| ------------- | ------------- |
| `PASS` | The test run successfully with the expected outcome. |
| `FAIL` | The test did not produce the expected outcome, so the test failed.|
| `ERROR`| While running the test an unexpected Error occurred. This is most likely the case, wif the test raised some Exception. |

Each test prints besides the status also the time which it took to execute the test. \
After all tests are run, a test summary is printed which shows the counts of each state in the run. This means how many test succeeded, failed or had an error.

#### Examples: Tests from command line
Each test can also be run independently from the command line with the command `--select`. The command selects all the tests which contain the substring followed afterwards. E.g. the following command runs all the tests which contain the keyword light in their name.

```sh
python test_smart_house.py --select light 
```
Furthermore, to run all tests and show also the variables which start with `test_` the command `--verbose` shows firstly all the variables and executes all the test in `test_smart_house.py`

Example usage: 

```sh
python test_smart_house.py --verbose
```

#### Test descriptions


<details><Summary> Template for test description </Summary>

```md
Name: test_name
Function: name_of_the_function 
Description: Short description of the test
```

</details>


### Device

```md
Name: test_toggle_status_from_off_to_on
Function: toggle_status
Description: Checks if calling toggle_status on a device with the status 'off' changes its status to 'on'. 
```

```md
Name: test_toggle_status_from_on_to_off
Function: toggle_status
Description: Checks if calling toggle_status on a device with the status 'on' changes its status to 'off'. 
```

```md
Name: test_toggle_status_with_invalid_status_raises_error
Function: toggle_status
Description: Checks if calling toggle_status on a device with an invalid status raises an AttributeError. 
```

```md
Name: test_abstract_methods_on_base_device_raises_error
Functions: get_power_consumption, describe_device
Description: Makes sure that the base Device class behaves like an abstract class. Verifies that calling placeholder methods get_power_consumption and describe_device directly on a base Device object raises a NotImplementedError.
```


### Connectable

```md
Name: test_connectable_default
Functions: new_connectable, is_connected
Description: Checks default state of a newly create Connectable object, which should be False for the connection status and have an empty string as the IP address.
```

```md
Name: test_connect_method
Functions: connect, is_connected
Description: Tests the 'connect' method by calling it with a test ip address and then asserts that the connection status became True and that the ip attribute got updated with the test ip.
```

```md
Name: test_disconnect_method
Functions: disconnect, is_connected
Description: Tests the 'disconnect' method. First it connects an object, then disconnects it, then asserts that the connection status reverted back to False. It also verifies that the ip address stays even after disconnecting.
```


### call

```md
Name: test_call_method_with_no_args
Function: call
Description: Tests the 'call' function with the method 'toggle_status', which takes no arguments.
```

```md
Name: test_call_method_with_args
Function: call
Description: Tests the 'call' function with the method 'connect', which takes arguments.
```

```md
Name: test_call_method_and_check_return_value
Function: call
Description: Tests that the 'call' function correctly return the value from the method that is executed. Checks the boolean value 'is_connected' before and after changing the state of the object.
```


### find

```md
Name: test_find_method_in_child_class
Function: find
Description: Checks if 'find' can find a method (describe_device) that is defined inside a child class (Light).
```

```md
Name: test_find_method_in_single_parent
Function: find
Description: For single inheritance. Checks if 'find' can find a method (toggle_status) in a parent class (Device) when called on a child object (Light).
```

```md
Name: test_find_method_in_multiple_parents
Function: find
Description: For multiple inheritance. Uses a 'Thermostat' object and checks if 'find' can find methods from both of its parent classes (Device, Connectable).
```


### Light

```md
Name: test_get_power_consumption_light_toggled_off
Function: get_power_consumption_light
Description: Tests if the power consumption is 0 if the device is toggled off. 
```


```md
Name: test_get_power_consumption_light_toggled_on
Function: get_power_consumption_light 
Description: This test checks if the power consumption is calculated correctly by comparing the calculated value to the expected value, which is 8.0 in this case. The test only works if the light is toggled on.
```

```md
Name: test_get_power_consumption_light_toggled_on_with_invalid_brightness
Function: get_power_consumption_light 
Description: This test checks if the power consumption is calculated correctly even if the base_power value is set incorrectly to 0 comparing the calculated value to the expected value, which is 0.0. The test works if the light is toggled on however there is some ambiguity because the same result would also be if the device is toggled off. 
```

```md
Name: test_describe_light_status_off
Function: describe_light 
Description: Checks if certain substrings are in the returned description off the light. The checked substrings are the status, name, location the the brightness is %.
```

```md
Name: test_describe_light_status_on
Function: describe_light 
Description: Checks if the certain substring of the status is in the returned description string. This test is limited because the other parameters are checked also in another test.
```

### Thermostat

```md
Name: test_get_power_consumption_thermostat_with_power_on
Function: get_power_consumption
Description: It checks if the expected calculated power consumption value of the thermostat is returned when the thermostat mock object is toggled on.
```

```md
Name: test_get_power_consumption_thermostat_with_power_on_target_current_same_value
Function: get_power_consumption
Description: It checks if the power consumption value is correctly calculated, if both target and current value is the same. So the expected power consumption is 0.
```

```md
Name: test_get_power_consumption_thermostat_with_power_off
Function: get_power_consumption
Description: It checks if the power consumption value is 0, when the device is toggled off.
```

```md
Name: test_describe_thermostat_with_active_connection
Function: describe_thermostat
Description: Tests if the description function of the thermostat is returned correctly, if the thermostat is connected by checking substring "connected to server".
```


```md
Name: test_describe_thermostat_no_connection
Function: describe_thermostat
Description: Tests if the description function of the thermostat is returned correctly, if the thermostat is not connected by checking substring "disconnected". Additionally other substrings such as the thermostat name and the current status substring.
```

```md
Name: test_set_target_temperature
Function: set_target_temperature
Description: Tests if the target temperature of the Thermostat mock object is correctly set, by calling the function set_target_temperature and then checking then the variable directly in the object. This is done, by the keyword "target_temperature" of the Thermostat object.
```


```md
Name: test_get_set_target_temperature
Function: get_target_temperature
Description: Tests if the target temperature of the Thermostat mock object is correctly returned and asserted to the default value of the mock object.
```


### Camera

```md
Name: test_camera_power_consumption_when_off
Function: get_power_consumption_camera
Description: Checks that the camera's power consumption is 0.0 when status is 'off'.
```

```md
Name: test_camera_power_consumption_when_on
Function: get_power_consumption_camera
Description: Checks that when the camera is 'on', the power consumption is correctly calculated (base_power multiplied by resolution_factor).
```

```md
Name: test_camera_describe_resolution_levels
Function: describe_camera
Description: Tests the output of the descriptions for all 3 possible resolution levels. Checks that the correct string ("low resolution", "medium resolution", or "high resolution") appears in the description based on 'resolution_factor'.
```

```md
Name: test_camera_describe_connection_status
Function: describe_camera
Description: Checks if the camera's description matches its connection status by looking for the "disconnected" message or for the "connected to server..." message.
```


### SmartHouseManagement

```md
Name: test_manager_calc_total_power_when_all_off
Function: calculate_total_power_consumption
Description: Checks that the total power consumption is 0 when all mock devices are in their default 'off' state.
```

```md
Name: test_manager_filter_by_room
Function: calculate_total_power_consumption
Description: Uses the 'Moodlamp' instance from smart_house.py to check if the manager correctly calculates total power consumption for a specific room based on all devices in that room. Checks that rooms without active devices return 0.
```

```md
Name: test_manager_get_connected_devices
Function: get_all_connected_devices
Description: Uses the 'ThermostatBedroom' instance from smart_house.py. Turns it on and connects it, checking that its name appears in the manager’s connected device report. Also checks if filtering by an incorrect IP outputs “No connections available.”
```

## Declaration of use of generative AI
No one in our team has used generative AI to complete this assignment. 