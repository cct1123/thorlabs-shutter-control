"""Opt-in vendor boundary check: loads real DLLs and enumerates USB, never connects.

Set KINESIS_TEST_DIR to the SDK folder. Other tests always use the software double.
"""

import os

import pytest

from thorlabs_shutter_control import KSC101Controller


@pytest.mark.skipif(not os.environ.get("KINESIS_TEST_DIR"), reason="KINESIS_TEST_DIR not set")
def test_real_sdk_loads_and_exposes_controller_contract():
    controller = KSC101Controller(kinesis_dir=os.environ["KINESIS_TEST_DIR"])
    serials = controller.discover()
    assert all(len(s) == 8 and s.startswith("68") for s in serials)
    import clr

    device_type = clr.GetClrType(controller._sdk.device_type)
    members = {member.Name for member in device_type.GetMembers()}
    required = {
        "CreateKCubeSolenoid",
        "Connect",
        "Disconnect",
        "StartPolling",
        "StopPolling",
        "PollingDuration",
        "IsSettingsInitialized",
        "WaitForSettingsInitialized",
        "GetDeviceInfo",
        "IsConnected",
        "USBConnected",
        "CommsStatus",
        "RequestStatus",
        "GetStatusBits",
        "GetSolenoidState",
        "GetOperatingState",
        "GetOperatingMode",
        "SetOperatingMode",
        "SetOperatingState",
        "EnableDevice",
        "Status",
    }
    assert required <= members
    enums = controller._sdk.enums
    assert str(enums.OperatingModes.Manual) == "Manual"
    assert str(enums.OperatingStates.Active) == "Active"
    assert str(enums.OperatingStates.Inactive) == "Inactive"
    status_properties = {prop.Name for prop in clr.GetClrType(enums).GetProperties()}
    assert "KeyEnabled" in status_properties
