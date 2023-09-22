"""Tests for MyBMWVehicle."""
import datetime

import pytest
import respx

from bimmer_connected.const import ATTR_ATTRIBUTES, ATTR_STATE, CarBrands
from bimmer_connected.models import GPSPosition, StrEnum, VehicleDataBase
from bimmer_connected.vehicle import VehicleViewDirection
from bimmer_connected.vehicle.charging_sessions import ChargingBlock, ChargingType
from bimmer_connected.vehicle.const import DriveTrainType
from bimmer_connected.vehicle.reports import CheckControlMessageReport

from . import (
    VIN_F31,
    VIN_G01,
    VIN_G20,
    VIN_G26,
    VIN_G70,
    VIN_I01_NOREX,
    VIN_I01_REX,
    VIN_I20,
    VIN_U11,
    get_deprecation_warning_count,
)
from .conftest import prepare_account_with_vehicles

ATTRIBUTE_MAPPING = {
    "remainingFuel": "remaining_fuel",
    "position": "gps_position",
    "cbsData": "condition_based_services",
    "checkControlMessages": "check_control_messages",
    "doorLockState": "door_lock_state",
    "updateReason": "last_update_reason",
    "chargingLevelHv": "charging_level_hv",
    "chargingStatus": "charging_status",
    "maxRangeElectric": "max_range_electric",
    "remainingRangeElectric": "remaining_range_electric",
    "parkingLight": "parking_lights",
    "remainingRangeFuel": "remaining_range_fuel",
    "updateTime": "timestamp",
    "chargingTimeRemaining": "charging_time_remaining",
}


@pytest.mark.asyncio
async def test_drive_train(caplog, bmw_fixture: respx.Router):
    """Tests around drive_train attribute."""
    account = await prepare_account_with_vehicles()
    vehicle = account.get_vehicle(VIN_F31)
    assert DriveTrainType.COMBUSTION == vehicle.drive_train

    vehicle = account.get_vehicle(VIN_G01)
    assert DriveTrainType.PLUGIN_HYBRID == vehicle.drive_train

    vehicle = account.get_vehicle(VIN_G26)
    assert DriveTrainType.ELECTRIC == vehicle.drive_train

    vehicle = account.get_vehicle(VIN_I01_NOREX)
    assert DriveTrainType.ELECTRIC == vehicle.drive_train

    vehicle = account.get_vehicle(VIN_I01_REX)
    assert DriveTrainType.ELECTRIC_WITH_RANGE_EXTENDER == vehicle.drive_train

    vehicle = account.get_vehicle(VIN_U11)
    assert DriveTrainType.ELECTRIC == vehicle.drive_train

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_parsing_attributes(caplog, bmw_fixture: respx.Router):
    """Test parsing different attributes of the vehicle."""
    account = await prepare_account_with_vehicles()

    for vehicle in account.vehicles:
        print(vehicle.name)
        assert vehicle.drive_train is not None
        assert vehicle.name is not None
        assert isinstance(vehicle.brand, CarBrands)
        assert vehicle.has_combustion_drivetrain is not None
        assert vehicle.has_electric_drivetrain is not None
        assert vehicle.drive_train_attributes is not None
        assert vehicle.is_charging_plan_supported is not None
        assert vehicle.is_charging_sessions_supported is not None
        assert vehicle.is_charging_statistics_supported is not None

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_drive_train_attributes(caplog, bmw_fixture: respx.Router):
    """Test parsing different attributes of the vehicle."""
    account = await prepare_account_with_vehicles()

    vehicle_drivetrains = {
        VIN_F31: (True, False),
        VIN_G01: (True, True),
        VIN_G20: (True, False),
        VIN_G26: (False, True),
        VIN_G70: (False, True),
        VIN_I01_NOREX: (False, True),
        VIN_I01_REX: (True, True),
        VIN_I20: (False, True),
        VIN_U11: (False, True),
    }

    for vehicle in account.vehicles:
        assert vehicle_drivetrains[vehicle.vin][0] == vehicle.has_combustion_drivetrain
        assert vehicle_drivetrains[vehicle.vin][1] == vehicle.has_electric_drivetrain

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_parsing_of_lsc_type(caplog, bmw_fixture: respx.Router):
    """Test parsing the lsc type field."""
    account = await prepare_account_with_vehicles()

    for vehicle in account.vehicles:
        assert vehicle.lsc_type is not None

    assert len(get_deprecation_warning_count(caplog)) == 0


def test_car_brand(caplog, bmw_fixture: respx.Router):
    """Test CarBrand enum."""
    assert CarBrands("BMW") == CarBrands("bmw")

    with pytest.raises(ValueError):
        CarBrands("Audi")

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_get_is_tracking_enabled(caplog, bmw_fixture: respx.Router):
    """Test setting observer position."""
    account = await prepare_account_with_vehicles()
    vehicle = account.get_vehicle(VIN_I01_REX)
    assert vehicle.is_vehicle_tracking_enabled is False

    vehicle = account.get_vehicle(VIN_F31)
    assert vehicle.is_vehicle_tracking_enabled is True

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_available_attributes(caplog, bmw_fixture: respx.Router):
    """Check that available_attributes returns exactly the arguments we have in our test data."""
    account = await prepare_account_with_vehicles()

    vehicle = account.get_vehicle(VIN_F31)
    assert ["gps_position", "vin"] == vehicle.available_attributes

    vehicle = account.get_vehicle(VIN_G01)
    assert [
        "gps_position",
        "vin",
        "remaining_range_total",
        "mileage",
        "charging_time_remaining",
        "charging_start_time",
        "charging_end_time",
        "charging_time_label",
        "charging_status",
        "connection_status",
        "remaining_battery_percent",
        "remaining_range_electric",
        "last_charging_end_result",
        "ac_current_limit",
        "charging_target",
        "charging_mode",
        "charging_preferences",
        "is_pre_entry_climatization_enabled",
        "remaining_fuel",
        "remaining_range_fuel",
        "remaining_fuel_percent",
        "condition_based_services",
        "check_control_messages",
        "door_lock_state",
        "timestamp",
        "lids",
        "windows",
    ] == vehicle.available_attributes

    vehicle = account.get_vehicle(VIN_G26)
    assert [
        "gps_position",
        "vin",
        "remaining_range_total",
        "mileage",
        "charging_time_remaining",
        "charging_start_time",
        "charging_end_time",
        "charging_time_label",
        "charging_status",
        "connection_status",
        "remaining_battery_percent",
        "remaining_range_electric",
        "last_charging_end_result",
        "ac_current_limit",
        "charging_target",
        "charging_mode",
        "charging_preferences",
        "is_pre_entry_climatization_enabled",
        "condition_based_services",
        "check_control_messages",
        "door_lock_state",
        "timestamp",
        "lids",
        "windows",
    ] == vehicle.available_attributes

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_vehicle_image(caplog, bmw_fixture: respx.Router):
    """Test vehicle image request."""
    vehicle = (await prepare_account_with_vehicles()).get_vehicle(VIN_G01)

    bmw_fixture.get(
        path__regex=r"(.*)/eadrax-ics/v3/presentation/vehicles/\w*/images",
        params={"carView": "FrontView"},
        headers={"accept": "image/png"},
    ).respond(200, content="png_image")
    assert b"png_image" == await vehicle.get_vehicle_image(VehicleViewDirection.FRONT)

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_no_timestamp(bmw_fixture: respx.Router):
    """Test no timestamp available."""
    vehicle = (await prepare_account_with_vehicles()).get_vehicle(VIN_F31)
    vehicle.data[ATTR_STATE].pop("lastFetched")
    vehicle.data[ATTR_ATTRIBUTES].pop("lastFetched")

    assert vehicle.timestamp is None


def test_strenum(caplog):
    """Tests StrEnum."""

    class TestEnum(StrEnum):
        """Test StrEnum."""

        HELLO = "HELLO"

    assert TestEnum("hello") == TestEnum.HELLO
    assert TestEnum("HELLO") == TestEnum.HELLO

    with pytest.raises(ValueError):
        TestEnum("WORLD")

    class TestEnumUnkown(StrEnum):
        """Test StrEnum with UNKNOWN value."""

        HELLO = "HELLO"
        UNKNOWN = "UNKNOWN"

    assert TestEnumUnkown("hello") == TestEnumUnkown.HELLO
    assert TestEnumUnkown("HELLO") == TestEnumUnkown.HELLO

    assert len([r for r in caplog.records if r.levelname == "WARNING"]) == 0
    assert TestEnumUnkown("WORLD") == TestEnumUnkown.UNKNOWN
    assert len([r for r in caplog.records if r.levelname == "WARNING"]) == 1


def test_vehiclebasedata():
    """Tests VehicleBaseData."""
    with pytest.raises(NotImplementedError):
        VehicleDataBase._parse_vehicle_data({})

    # CheckControlMessageReport does not override parent methods from_vehicle_data()
    ccmr = CheckControlMessageReport.from_vehicle_data(
        {"state": {"checkControlMessages": [{"severity": "LOW", "type": "ENGINE_OIL"}]}}
    )
    assert len(ccmr.messages) == 1
    assert ccmr.has_check_control_messages is False


def test_gpsposition():
    """Tests around GPSPosition."""
    pos = GPSPosition(1.0, 2.0)
    assert pos == GPSPosition(1, 2)
    assert pos == {"latitude": 1.0, "longitude": 2.0}
    assert pos == (1, 2)
    assert pos != "(1, 2)"
    assert pos[0] == 1


@pytest.mark.asyncio
async def test_charging_statistics(caplog, bmw_fixture: respx.Router):
    """Test if the parsing of charging statistics is working."""

    # Car with no statistics
    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_F31)
    assert status.charging_statistics == None
    assert status.is_charging_statistics_supported == False

    # Car with statistics
    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_U11)
    assert status.is_charging_statistics_supported == True

    status = status.charging_statistics
    assert status.charging_session_timeperiod == "September 2023"
    assert status.charging_session_count == 6
    assert status.total_energy_charged == 168

    assert len(get_deprecation_warning_count(caplog)) == 0


@pytest.mark.asyncio
async def test_charging_sessions(caplog, bmw_fixture: respx.Router):
    """Test if the parsing of charging sessions is working."""

    # Car with no sessions
    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_F31)
    assert status.charging_sessions == None
    assert status.is_charging_sessions_supported == False

    # Car with sessions
    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_U11)
    assert status.is_charging_sessions_supported == True

    status = status.charging_sessions
    assert status.charging_session_count == len(status.charging_sessions)
    assert status.charging_sessions[0].status == "FINISHED"
    assert status.charging_sessions[0].description == "9/3/2023 15:47 • some_road • duration • -- EUR"
    assert status.charging_sessions[0].address == "Some Street 999 99999 Somecity"
    assert status.charging_sessions[0].charging_type == ChargingType.AC_HIGH
    assert status.charging_sessions[0].soc_start == 0.1
    assert status.charging_sessions[0].soc_end == 0.62
    assert status.charging_sessions[0].energy_charged == 37.7
    assert status.charging_sessions[0].time_start == datetime.datetime(2023, 3, 9, 15, 47)
    assert status.charging_sessions[0].time_end == datetime.datetime(2023, 3, 9, 17, 38)
    assert status.charging_sessions[0].duration == 109
    assert status.charging_sessions[0].power_avg == 20.48
    assert status.charging_sessions[0].power_min == 0.0
    assert status.charging_sessions[0].power_max == 21.55
    assert status.charging_sessions[0].public is True
    assert status.charging_sessions[0].pre_condition is True
    assert status.charging_sessions[0].mileage == 9999

    # ChargingBlocks Exists
    assert len(status.charging_sessions[0].charging_blocks) == 24
    assert (isinstance(x, ChargingBlock) for x in status.charging_sessions[0].charging_blocks)
    assert status.charging_sessions[0].charging_blocks[0].time_start == "2023-09-03T15:47:47Z"
    assert status.charging_sessions[0].charging_blocks[0].time_end == "2023-09-03T15:47:48Z"
    assert status.charging_sessions[0].charging_blocks[0].power_avg == 0.0

    # Missing ChargingBlocks, failed charge
    assert len(status.charging_sessions[5].charging_blocks) == 0
    assert status.charging_sessions[5].power_avg == 0.0
    assert status.charging_sessions[5].power_min == 0.0
    assert status.charging_sessions[5].power_max == 0.0

    assert len(get_deprecation_warning_count(caplog)) == 0


def test_charging_type():
    """Test charging types are handled correctly."""

    charging_type = ChargingType("DC")
    assert charging_type == ChargingType.DC

    charging_type = ChargingType("AC_HIGH")
    assert charging_type == ChargingType.AC_HIGH

    unknown_charging_type = ChargingType("SUPER_DUPER_HYPER_CHARGER")
    assert unknown_charging_type == ChargingType.UNKNOWN


@pytest.mark.asyncio
async def test_headunit_data(caplog, bmw_fixture: respx.Router):
    """Test if the parsing of headunit is working."""

    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_I20).headunit

    assert status.idrive_version == "ID8"
    assert status.headunit_type == "MGU"
    assert status.software_version == "07/2021.00"

    status = (await prepare_account_with_vehicles()).get_vehicle(VIN_F31).headunit

    assert status.idrive_version == "ID4"
    assert status.headunit_type == "NBT"
    assert status.software_version == "11/2013.02"

    assert len(get_deprecation_warning_count(caplog)) == 0
