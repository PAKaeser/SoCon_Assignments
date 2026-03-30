from typing import Callable, Any
import pprint

# static values for the dictionaries to reduce mental load and key errors
CLASSNAME_KEY = "_classname"
CLASS_KEY = "_class"
PARENT_KEY = "_parent"
NEW_KEY = "_new"


############################################
# Functions for interacting with the class #
############################################


def find(cls: dict, method_name: str) -> Callable:
    """Tries to recursively find the given method name in the current and parent class. I
    f the method is not found a NotImplementedError is raised. Handles also multiple inheritance.
    Params:
        cls (dict): Current class, in which the provided method name should be looked up
        method_name (str): Is the method name which should be looked up
    Returns:
        The found function (Callable) of the provided method name.
    """
    while cls is not None:
        if method_name in cls:
            return cls[method_name]

        parent = cls[PARENT_KEY]
        if parent is None:
            break
        elif isinstance(parent, tuple) or isinstance(parent, list):
            # Multiple inheritance
            for p in parent:
                try:
                    return find(p, method_name)
                except NotImplementedError:
                    continue
            break
        else:
            # Single inheritance
            cls = parent
    raise NotImplementedError(method_name)


def call(cls: dict, method_name: str, *args, **kwargs) -> Any:
    """Calls the provided method name in the class dictionary.
    Params:
        cls (dict): Current class dictionary, in which the provided method name should be looked up
        method_name (str): Is the method name which should be looked up
        *args: List of arguments for the target function
        **kwargs: Dictionary for keywords arguments for the target function
    Returns:
        The callback result which can be anything.
    """
    method = find(cls[CLASS_KEY], method_name)
    return method(cls, *args, **kwargs)


def make(cls, *args) -> dict:
    """Executes the initialize function of the class with the provided arguments.
    Params:
        cls (dict): Class dictionary, which should be instantiated.
        *args: List of arguments which should be inserted into the class.
    Returns:
        A dictionary object which represents the instantiated class object.
    """
    return cls[NEW_KEY](*args)


########################
# Parent class: Device #
########################


def get_power_consumption(cls, *_):
    if cls[CLASS_KEY] is Device:
        raise NotImplementedError(
            "get_power_consumption should be defined in the specific device"
        )
    return cls[CLASS_KEY]["get_power_consumption"](cls)


def describe_device(cls: dict, *_):
    if cls[CLASS_KEY] is Device:
        raise NotImplementedError(
            "Device description should be defined in the specific device"
        )
    return cls[CLASS_KEY]["describe_device"](cls)


def toggle_status(cls: dict) -> dict:
    """Toggles the status of the current device. Maps 'on' → 'off', and 'off' → 'on'.
    If an unknown status is found, an AttributeError is raised.
    Params:
        cls (dict): Is the device dictionary which contains the current status.
    Returns:
        A dictionary with the updated status.
    """
    match cls["status"]:
        case "on":
            new_status = "off"
        case "off":
            new_status = "on"
        case _:
            raise AttributeError(
                f"Status {cls['status']} not recognized. Possible status of device is either 'on' or 'off'."
            )
    cls["status"] = new_status
    return {"status": new_status}


def new_device(name: str, location: str, base_power: float, status: str) -> dict:
    """Function to create a new device by setting the expected class attributes.
    Params:
        name (str): Name of the new device
        location (location): Location of the new device
        base_power (float): Is the base operating power for this device
        status (str): Describes the status of the device, which can be either on or off
    """
    return {
        "name": name,
        "location": location,
        "base_power": base_power,
        "status": status,
        CLASS_KEY: Device,
    }


Device = {
    CLASSNAME_KEY: "Device",
    PARENT_KEY: [],
    "get_power_consumption": get_power_consumption,
    "describe_device": describe_device,
    "toggle_status": toggle_status,
    NEW_KEY: new_device,
}


#############################
# Parent class: Connectable #
#############################


def connect(cls: dict, ip: str) -> None:
    """Connects this object to the specified ip address."""
    cls["ip"] = ip
    cls["connected"] = True


def disconnect(cls: dict) -> None:
    """Disconnects this object from the connection."""
    cls["connected"] = False


def is_connected(cls: dict):
    """Returns the current connection status."""
    return cls["connected"]


def new_connectable(connected: bool = False, ip: str = "") -> dict:
    """Function to create a new connectable by setting the expected class attributes. By default all new objects are disconnected.
    Params:
        connected (bool): Connection status, either true or false
        ip (str): Address to which current object is connected to
    """
    return {"connected": connected, "ip": ip, CLASS_KEY: Connectable}


Connectable = {
    CLASSNAME_KEY: "Connectable",
    PARENT_KEY: [],
    NEW_KEY: new_connectable,
    "disconnect": disconnect,
    "is_connected": is_connected,
    "connect": connect,
}


###################
# Subclass: Light #
###################


def get_power_consumption_light(cls: dict) -> float:
    """Calculates the power consumption of the light according to provided formula in the assignment.
    It multiplies the base power by the brightness divided by 100 and rounds the result. It computes this only if the device is on.
    Params:
        cls (dict): The current light dictionary which holds the values for the base power and brightness.
    Returns:
        The power consumption as a float.
    """
    if cls["status"] != "on":
        return 0.0
    consumption = round(cls["base_power"] * (cls["brightness"] / 100))
    return consumption


def describe_light(cls: dict) -> str:
    """Returns the description of the current light.
    Params:
        cls (dict): The current light dictionary.
    """
    description = f"""The {cls["name"]} is located in the {cls["location"]}, is currently {cls["status"]}, and is
    currently set to {cls["brightness"]}% brightness."""
    return description


def new_light(
    name: str, location: str, base_power: float, status: str, brightness: int
) -> dict:
    """Function to crete a new light object.
    Params:
        name (str): Name of the device
        location (str): Location of the device
        base_power (float): The base power consumption of the device
        status (str): Status of the device, if it is turned on or off
        brightness (int): The brightness of the light
    """
    device_parent_class_init = make(Device, name, location, base_power, status)
    new_light = {CLASS_KEY: Light, "brightness": brightness}
    return device_parent_class_init | new_light


Light = {
    CLASSNAME_KEY: "Light",
    PARENT_KEY: [Device],
    NEW_KEY: new_light,
    "get_power_consumption": get_power_consumption_light,
    "describe_device": describe_light,
}


########################
# Subclass: Thermostat #
########################


def get_power_consumption_thermostat(cls: dict) -> float:
    """Calculates the power consumption of the current thermostat according to provided formula in the assignment.
    It multiplies the base power by the absolute value of the temperature difference. It computes this only if the device is on.
    Params:
        cls (dict): The current thermostat dictionary which holds the values for the base power, target and room temperature
    Returns:
        The power consumption as a float
    """
    if cls["status"] != "on":
        return 0.0
    consumption = cls["base_power"] * abs(
        cls["target_temperature"] - cls["room_temperature"]
    )
    return consumption


def describe_thermostat(cls: dict) -> str:
    """Returns the description of the current thermostat.
    Params:
        cls (dict): The current thermostat dictionary.
    """
    description = f"""The {cls["name"]} is located in the {cls["location"]}, is currently {cls["status"]}, and is
    currently set to {cls["target_temperature"]} degrees Celsius in an {cls["room_temperature"]} degree room. """

    if cls["connected"]:
        description += f"It is currently connected to server {cls['ip']}"
    else:
        description += "It is currently disconnected."

    return description


def set_target_temperature(cls: dict, temperature: int) -> None:
    """Sets the target temperature of the thermostat.
    Params:
        cls (dict): The thermostat dictionary.
        temperature (int): The new target temperature.
    """
    cls["target_temperature"] = temperature


def get_target_temperature(cls: dict) -> int:
    """Gets the target temperature of the thermostat.
    Params:
        cls (dict): The thermostat dictionary.
    Returns:
        The target temperature as int.
    """
    return cls["target_temperature"]


def new_thermostat(
    name: str,
    location: str,
    base_power: float,
    status: str,
    room_temperature: int,
    target_temperature: int,
) -> dict:
    """Function to crete a new thermostat object.
    Params:
        name (str): Name of the device
        location (str): Location of the device
        base_power (float): The base power consumption of the device
        status (str): Status of the device, if it is turned on or off

        room_temperature (int): The current room temperature which the thermostat measures
        target_temperature (int): The target room temperature
    """
    device_parent_class_init = make(Device, name, location, base_power, status)
    connectable_parent_class_init = make(Connectable)
    new_thermostat = {
        CLASS_KEY: Thermostat,
        "room_temperature": room_temperature,
        "target_temperature": target_temperature,
    }
    return device_parent_class_init | connectable_parent_class_init | new_thermostat


Thermostat = {
    CLASSNAME_KEY: "Thermostat",
    PARENT_KEY: [Device, Connectable],
    NEW_KEY: new_thermostat,
    "get_power_consumption": get_power_consumption_thermostat,
    "describe_device": describe_thermostat,
    "set_target_temperature": set_target_temperature,
    "get_target_temperature": get_target_temperature,
}


####################
# Subclass: Camera #
####################


def get_power_consumption_camera(cls: dict) -> float:
    """Calculates the power consumption of the current camera according to provided formula in the assignment.
    It multiplies the base power by the resolution factor. It computes this only if the device is on.
    Params:
        cls (dict): The current camera dictionary which holds the values for the base power and resolution factor
    Returns:
        The power consumption as a float
    """
    if cls["status"] != "on":
        return 0.0
    consumption = cls["base_power"] * cls["resolution_factor"]
    return consumption


def describe_camera(cls: dict) -> str:
    """Returns the description of the current camera.
    Params:
        cls (dict): The current camera dictionary.
    """
    if cls["resolution_factor"] < 5:
        resolution = "low"
    elif cls["resolution_factor"] < 10:
        resolution = "medium"
    else:
        resolution = "high"

    description = f"""The {cls["name"]} is located in the {cls["location"]}, is currently {cls["status"]}, and has
    a {resolution} resolution sensor. """

    if cls["connected"]:
        description += f"""It is currently connected to server {cls["ip"]}"""
    else:
        description += """It is currently disconnected."""

    return description


def new_camera(
    name: str, location: str, base_power: float, status: str, resolution_factor: int
) -> dict:
    """Function to crete a new camera object.
    Params:
        name (str): Name of the device
        location (str): Location of the device
        base_power (float): The base power consumption of the device
        status (str): Status of the device, if it is turned on or off

        resolution_factor (int): The resolution factor of the camera
    """
    device_parent_class_init = make(Device, name, location, base_power, status)
    connectable_parent_class_init = make(Connectable)
    new_camera = {CLASS_KEY: Camera, "resolution_factor": resolution_factor}
    return device_parent_class_init | connectable_parent_class_init | new_camera


Camera = {
    CLASSNAME_KEY: "Camera",
    PARENT_KEY: [Device, Connectable],
    NEW_KEY: new_camera,
    "get_power_consumption": get_power_consumption_camera,
    "describe_device": describe_camera,
}


######################################
##   Class: SmartHouseManagement    ##
######################################


def new_smart_house_management():
    """Function to create a SmartHouseManagement class"""
    return {CLASS_KEY: SmartHouseManagement}


def search(glob=None, search_type=None, search_room=None):
    """helper function to reduce code redundancy in methods of SmartHouseManagement"""
    # available_devices is list with class dicts with parent 'Device from globals
    if glob == None:
        glob = globals()
    available_devices = [
        glob[x]
        for x in glob
        if isinstance(glob[x], dict)
        and PARENT_KEY in glob[x]
        and (
            True
            if [
                element
                for element in glob[x][PARENT_KEY]
                if element[CLASSNAME_KEY] == "Device"
            ]
            else False
        )
    ]
    if search_type in available_devices:
        # creates a dictonary based on instances in global, using fact that instances have a name and compares search_type with class of instance
        dictionary = {
            x: glob[x]
            for x in glob
            if isinstance(glob[x], dict)
            and "name" in glob[x]
            and glob[x][CLASS_KEY] == search_type
        }
    else:
        # if search_type not a device, dictionary stores all devices
        dictionary = {
            x: glob[x] for x in glob if isinstance(glob[x], dict) and "name" in glob[x]
        }

    if search_room is not None:
        # updates dictionary for search room, uses convenience  of dictionary already created from globals to not check isinstance again
        dictionary = {
            x: dictionary[x]
            for x in dictionary
            if dictionary[x]["location"] == search_room
        }
    return dictionary


def calculate_total_power_consumption(
    cls: dict, glob=None, search_type=None, search_room=None
):
    """Function to calculate total power consumption
    Params:
        search_type: can be set to specific device subclass
        search_room: can be set to specific room name
    """
    filtered_dict = search(glob, search_type, search_room)
    power_consumption_adder = 0
    for element in filtered_dict:
        power_consumption_adder += get_power_consumption(filtered_dict[element])
    return power_consumption_adder


def get_all_device_description(
    cls: dict, glob=None, search_type=None, search_room=None
):
    """Function to describe all Devices for type and room"""
    filtered_dict = search(glob, search_type, search_room)
    res = ""
    for element in filtered_dict:
        res = res + describe_device(filtered_dict[element]) + "\n"

    return res


def get_all_connected_devices(cls: dict, glob=None, ip=None):
    # available_connectables is list of classes with parents connectable from globals, done this way to ensure future additional connectables are also in list
    if glob is None:
        glob = globals()
    available_connectables = [
        globals()[x]
        for x in globals()
        if isinstance(globals()[x], dict)
        and PARENT_KEY in globals()[x]
        and (
            True
            if [
                element
                for element in globals()[x][PARENT_KEY]
                if element[CLASSNAME_KEY] == "Connectable"
            ]
            else False
        )
    ]
    # filtered_dict is dict of instances with parentclass connectable and status on and connection True
    filtered_dict = {
        x: glob[x]
        for x in glob
        if isinstance(glob[x], dict)
        and "name" in glob[x]
        and glob[x][CLASS_KEY] in available_connectables
        and glob[x]["status"] == "on"
        and glob[x]["connected"]
    }
    if ip:
        filtered_dict = {
            x: filtered_dict[x] for x in filtered_dict if filtered_dict[x]["ip"] == ip
        }
    if filtered_dict == {}:
        return "No connections available"
    res = "Connection to following Devices: \n"
    for element in filtered_dict:
        res = (
            res
            + describe_device(filtered_dict[element])
            + " The power consumption is "
            + str(get_power_consumption(filtered_dict[element]))
            + "."
        )
    return res


SmartHouseManagement = {
    CLASSNAME_KEY: "SmartHouseManagement",
    PARENT_KEY: [],
    NEW_KEY: new_smart_house_management,
    "calculate_total_power_consumption": calculate_total_power_consumption,
    "get_all_device_description": get_all_device_description,
    "get_all_connected_devices": get_all_connected_devices,
}


######################
##    Instances     ##
######################


def create_instances() -> None:
    """Creates global instances to show the functionalities of the smart house."""
    global mood_lamp
    global thermostat_entrance
    global security_camera
    global home_management

    mood_lamp = make(Light, "Moodlamp", "bedroom", 100, "off", 2)
    thermostat_entrance = make(
        Thermostat, "Thermostat Entrance", "Entrance", 20, "off", 20, 10
    )
    security_camera = make(Camera, "Security Camera 1", "Entrance", 200, "off", 8)
    home_management = make(SmartHouseManagement)


def print_instances():
    """Prints information about the created instances."""
    create_instances()
    print("====== Print instances ======")
    call(mood_lamp, "toggle_status")
    print(describe_device(mood_lamp))
    print(
        f"The power consumption of the Moodlamp in the bedroom is: {get_power_consumption(mood_lamp)}\n"
    )

    call(thermostat_entrance, "toggle_status")
    call(thermostat_entrance, "connect", "001.001.001.10")
    print(
        f"The temperature for the thermostat in the entrance is set for: {get_target_temperature(thermostat_entrance)} degrees"
    )
    call(thermostat_entrance, "set_target_temperature", 18)
    print(call(thermostat_entrance, "describe_device"))
    print(
        f"The power consumption of the thermostat in the entrance is: {get_power_consumption(thermostat_entrance)}\n"
    )

    call(security_camera, "toggle_status")

    call(security_camera, "connect", "001.001.001.11")

    print(call(security_camera, "describe_device"), "\n")

    print("disconnecting thermostat, \nchecking connectables:")
    call(thermostat_entrance, "disconnect")
    print(
        f"The Thermostat is currently{'' if call(thermostat_entrance, 'is_connected') else ' not'} connected"
    )
    print(
        f"The SecurityCamera is currently{'' if call(security_camera, 'is_connected') else ' not'} connected \n"
    )
    print("Disconnecting security camera\n")
    call(security_camera, "disconnect")

    print(
        "Print home management with search type None and search room entrance:\n",
        call(
            home_management,
            "get_all_device_description",
            search_type=None,
            search_room="Entrance",
        ),
    )
    print(
        "Print get all connected devices:\n",
        call(home_management, "get_all_connected_devices"),
    )
    print(
        "Print get all connected devices:\n",
        call(home_management, "get_all_connected_devices"),
    )
    print(
        "Print calculate total power consumption with search type Light and search room Entrance\n(should be 0 since there is no light instance in Entrance):",
        call(
            home_management,
            "calculate_total_power_consumption",
            search_type=Light,
            search_room="Entrance",
        ),
        "\n",
    )


def filter_all_device_instances(glob: dict) -> list[dict]:
    """Filters the devices and connectable instances from the provided global dict. It returns a list with all the instances.
    Params:
        glob (dict): Dictionary created from globals() function
    Returns:
        A list of instances which fulfill the requirements of a instantiated device.
    """
    output_devices = []
    for instance_value in glob.values():
        if isinstance(instance_value, dict) and instance_value:
            if CLASS_KEY in instance_value:
                if instance_value[CLASS_KEY][PARENT_KEY]:
                    output_devices.append(instance_value)
    return output_devices


def energy_consumption_comparison(
    device_object_list: list[dict], smart_house_management: dict
):
    """Shows a comparison of the energy consumption if all devices are turned on and off.
    Params:
         device_object_list (list[dict]): Is a list of instances of devices, which can be toggled on and off
         smart_house_management (dict): An instance of the smart house management class, which has the function to calculate the total power consumption.
    """
    print("Toggle all devices on")
    for current_device in device_object_list:
        if current_device["status"] != "on":
            call(current_device, "toggle_status")
    print(
        f"Power consumption with all devices on: {call(smart_house_management, 'calculate_total_power_consumption')}"
    )
    print("Toggle all devices off")
    for current_device in device_object_list:
        if current_device["status"] == "on":
            call(current_device, "toggle_status")
    print(
        f"Power consumption with all devices off: {call(smart_house_management, 'calculate_total_power_consumption')}",
        "\n\n",
    )


if __name__ == "__main__":
    # Run the printing functions
    create_instances()
    print_instances()
    energy_consumption_comparison(
        device_object_list=filter_all_device_instances(globals()),
        smart_house_management=home_management,
    )
