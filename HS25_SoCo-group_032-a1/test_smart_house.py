import smart_house
import argparse
import time

STATE_PASS = "pass"
STATE_FAIL = "fail"
STATE_ERROR = "error"

test_1 = 1
test_2 = "2"
test_another_variable = [1, 2, 3]


def setup():
    # sets up multiple Instances used for testing
    global mock_device
    global mock_connectable
    global mock_light
    global mock_thermostat
    global mock_camera
    global mock_manager

    mock_device = smart_house.make(
        smart_house.Device, "Mock Device", "living room", 30, "off"
    )
    mock_connectable = smart_house.make(smart_house.Connectable)
    mock_light = smart_house.make(
        smart_house.Light, "Mock Light", "bedroom", 10, "off", 80
    )
    mock_thermostat = smart_house.make(
        smart_house.Thermostat, "Thermostat Bedroom", "bedroom", 20, "off", 0, 10
    )
    mock_camera = smart_house.make(
        smart_house.Camera, "Mock Camera", "hallway", 5, "off", 8
    )
    mock_manager = smart_house.make(smart_house.SmartHouseManagement)


def teardown():
    # removes all instances from setup
    del globals()["mock_device"]
    del globals()["mock_connectable"]
    del globals()["mock_light"]
    del globals()["mock_thermostat"]
    del globals()["mock_camera"]
    del globals()["mock_manager"]


# ------------------------
# Tests for Device [start]


def test_toggle_status_from_off_to_on():
    assert mock_device["status"] == "off"
    smart_house.call(mock_device, "toggle_status")
    assert mock_device["status"] == "on"


def test_toggle_status_from_on_to_off():
    mock_device["status"] = "on"
    assert mock_device["status"] == "on"
    smart_house.call(mock_device, "toggle_status")
    assert mock_device["status"] == "off"


def test_toggle_status_with_invalid_status_raises_error():
    mock_device["status"] = "some invalid status"
    error_raised = False
    try:
        smart_house.call(mock_device, "toggle_status")
    except AttributeError:
        error_raised = True
    assert error_raised, "AttributeError was not raised for an invalid status"


def test_abstract_methods_on_base_device_raises_error():
    power_error_raised = False
    describe_error_raised = False
    try:
        smart_house.call(mock_device, "get_power_consumption")
    except NotImplementedError:
        power_error_raised = True
    try:
        smart_house.call(mock_device, "describe_device")
    except NotImplementedError:
        describe_error_raised = True
    assert power_error_raised, "get_power_consumption did not raise NotImplementedError"
    assert describe_error_raised, "describe_device did not raise NotImplementedError"


# Tests for Device [end]
# ----------------------


# -----------------------------
# Tests for Connectable [start]


def test_connectable_default():
    assert not smart_house.call(mock_connectable, "is_connected")
    assert mock_connectable["ip"] == ""


def test_connect_method():
    test_ip = "10.10.10.4"
    smart_house.call(mock_connectable, "connect", test_ip)
    assert smart_house.call(mock_connectable, "is_connected")
    assert mock_connectable["ip"] == test_ip


def test_disconnect_method():
    test_ip = "10.10.10.4"
    smart_house.call(mock_connectable, "connect", test_ip)
    assert smart_house.call(mock_connectable, "is_connected")
    smart_house.call(mock_connectable, "disconnect")
    assert not smart_house.call(mock_connectable, "is_connected")
    assert mock_connectable["ip"] == test_ip


# Tests for Connectable [end]
# ---------------------------


# ----------------------
# Tests for call [start]


def test_call_method_with_no_args():
    assert mock_device["status"] == "off"
    smart_house.call(mock_device, "toggle_status")
    assert mock_device["status"] == "on"


def test_call_method_with_args():
    test_ip = "10.10.10.4"
    smart_house.call(mock_thermostat, "connect", test_ip)
    assert mock_thermostat["connected"]
    assert mock_thermostat["ip"] == test_ip


def test_call_method_and_check_return_value():
    assert not smart_house.call(mock_camera, "is_connected")
    smart_house.call(mock_camera, "connect", "10.10.10.4")
    assert smart_house.call(mock_camera, "is_connected")


# Tests for call [end]
# --------------------


# ----------------------
# Tests for find [start]


def test_find_method_in_child_class():
    found_method = smart_house.find(
        mock_light[smart_house.CLASS_KEY], "describe_device"
    )
    assert found_method == smart_house.describe_light


def test_find_method_in_single_parent():
    found_method = smart_house.find(mock_light[smart_house.CLASS_KEY], "toggle_status")
    assert found_method == smart_house.toggle_status


def test_find_method_in_multiple_parents():
    thermostat_class = mock_thermostat[smart_house.CLASS_KEY]
    device_method = smart_house.find(thermostat_class, "toggle_status")
    assert device_method == smart_house.toggle_status
    connectable_method = smart_house.find(thermostat_class, "connect")
    assert connectable_method == smart_house.connect


def test_find_nonexistent_method_raises_error():
    error_raised = False
    try:
        smart_house.find(mock_light[smart_house.CLASS_KEY], "non_existent_method")
    except NotImplementedError:
        error_raised = True
    assert error_raised, "NotImplementedError was not raised for a missing method"


# Tests for find [end]
# --------------------


# -----------------------
# Tests for Light [start]


def test_get_power_consumption_light_toggled_off():
    assert smart_house.get_power_consumption_light(mock_light) == 0.0


def test_get_power_consumption_light_toggled_on():
    smart_house.call(mock_light, "toggle_status")
    assert smart_house.get_power_consumption_light(mock_light) == 8.0


def test_get_power_consumption_light_toggled_on_with_invalid_brightness():
    smart_house.call(mock_light, "toggle_status")
    mock_light["base_power"] = 0
    assert smart_house.get_power_consumption_light(mock_light) == 0


def test_describe_light_status_off():
    light_description = smart_house.describe_light(mock_light)
    assert "is currently off" in light_description
    assert "Mock Light" in light_description
    assert "bedroom" in light_description
    assert "80%" in light_description


def test_describe_light_status_on():
    smart_house.call(mock_light, "toggle_status")
    light_description = smart_house.describe_light(mock_light)
    assert "is currently on" in light_description


# Tests for Light [end]
# ---------------------


# ----------------------------
# Tests for Thermostat [start]


def test_get_power_consumption_thermostat_with_power_on():
    smart_house.call(mock_thermostat, "toggle_status")
    power_consumption = smart_house.get_power_consumption(mock_thermostat)
    assert power_consumption == 200


def test_get_power_consumption_thermostat_with_power_on_target_current_same_value():
    smart_house.call(mock_thermostat, "toggle_status")
    smart_house.call(mock_thermostat, "set_target_temperature", 0)
    power_consumption = smart_house.get_power_consumption(mock_thermostat)
    assert power_consumption == 0.0


def test_get_power_consumption_thermostat_with_power_off():
    power_consumption = smart_house.get_power_consumption(mock_thermostat)
    assert power_consumption == 0.0


def test_describe_thermostat_with_active_connection():
    smart_house.call(mock_thermostat, "connect", "001.001.001.11")
    thermostat_description = smart_house.describe_thermostat(mock_thermostat)
    assert "connected to server" in thermostat_description


def test_describe_thermostat_no_connection():
    thermostat_description = smart_house.describe_thermostat(mock_thermostat)
    assert "disconnected" in thermostat_description
    assert "Thermostat Bedroom" in thermostat_description
    assert "is currently off" in thermostat_description


def test_set_target_temperature():
    smart_house.set_target_temperature(mock_thermostat, 40)
    assert mock_thermostat["target_temperature"] == 40


def test_get_set_target_temperature():
    assert smart_house.get_target_temperature(mock_thermostat) == 10


# Tests for Thermostat [end]
# --------------------------


# ------------------------
# Tests for Camera [start]


def test_camera_power_consumption_when_off():
    assert smart_house.call(mock_camera, "get_power_consumption") == 0.0


def test_camera_power_consumption_when_on():
    smart_house.call(mock_camera, "toggle_status")
    assert smart_house.call(mock_camera, "get_power_consumption") == 40


def test_camera_describe_resolution_levels():
    mock_camera["resolution_factor"] = 4
    assert "low resolution" in smart_house.call(mock_camera, "describe_device")
    mock_camera["resolution_factor"] = 7
    assert "medium resolution" in smart_house.call(mock_camera, "describe_device")
    mock_camera["resolution_factor"] = 12
    assert "high resolution" in smart_house.call(mock_camera, "describe_device")


def test_camera_describe_connection_status():
    description_off = smart_house.call(mock_camera, "describe_device")
    assert "It is currently disconnected" in description_off
    smart_house.call(mock_camera, "connect", "10.0.0.4")
    description_on = smart_house.call(mock_camera, "describe_device")
    assert "connected to server 10.0.0.4" in description_on


# Tests for Camera [end]
# ----------------------


# --------------------------------------
# Tests for SmartHouseManagement [start]


def test_manager_calc_total_power_when_all_off():
    total_power = smart_house.call(mock_manager, "calculate_total_power_consumption")
    assert total_power == 0


def test_manager_filter_by_room():
    mock_light["status"] = "off"
    smart_house.call(mock_light, "toggle_status")

    mock_thermostat["status"] = "off"
    smart_house.call(mock_thermostat, "toggle_status")

    total_in_bedroom = smart_house.call(
        mock_manager,
        "calculate_total_power_consumption",
        glob=globals(),
        search_room="bedroom",
    )
    assert total_in_bedroom == 208

    total_in_hallway = smart_house.call(
        mock_manager,
        "calculate_total_power_consumption",
        search_room="hallway",
    )
    assert total_in_hallway == 0


def test_manager_get_connected_devices():
    mock_thermostat["status"] = "on"
    smart_house.call(mock_thermostat, "connect", "1.1.1.1")
    description = smart_house.call(
        mock_manager, "get_all_connected_devices", glob=globals()
    )
    assert "Thermostat Bedroom" in description

    none_desc = smart_house.call(
        mock_manager, "get_all_connected_devices", ip="2.2.2.2"
    )
    assert none_desc == "No connections available"


# Tests for SmartHouseManagement [end]
# ------------------------------------


def run_tests(select=""):
    results = {STATE_PASS: [], STATE_FAIL: [], STATE_ERROR: []}
    filtered_globals = {
        name: test
        for name, test in globals().items()
        if name.startswith("test_") and select in name and callable(test)
    }
    print("--- INDIVIDUAL RESULTS ---")
    for name, func in filtered_globals.items():
        start_time = time.time()
        try:
            setup()
            func()
            elapsed_time = time.time() - start_time
            print(f"[PASS] {name} ({elapsed_time:.8f}s)")
            results[STATE_PASS].append(name)
        except AssertionError as e:
            elapsed_time = time.time() - start_time
            print(f"[*FAIL*] {name} ({elapsed_time:.8f}s) -> {e}")
            results[STATE_FAIL].append(name)
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[*ERROR*] {name} ({elapsed_time:.8f}s) -> {type(e).__name__}: {e}")
            results[STATE_ERROR].append(name)
        finally:  # This guarantees that teardown() always gets called
            teardown()
    print("\n--- SUMMARY ---")
    print(
        f"Pass: {len(results[STATE_PASS])}, Fail: {len(results[STATE_FAIL])}, Error: {len(results[STATE_ERROR])}"
    )


def list_variables_with_test_in_name():
    return sorted(
        name
        for name, value in globals().items()
        if name.startswith("test") and not callable(value)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--select", default="")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        print("--- VARIABLES WITH TEST IN NAME ---")
        for v in list_variables_with_test_in_name():
            print(v)
    run_tests(args.select)


if __name__ == "__main__":
    main()
