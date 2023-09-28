# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from vehicle import vehicle  # type: ignore
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vdb.types import TypedDataPointResult

# Get the app directory path
app_dir_path = os.path.abspath(os.path.join(__file__, "../../.."))

# Add the src directory to the sys.path
src_dir = os.path.join(app_dir_path, "src")
sys.path.insert(0, src_dir)

# Import the SeatAdjusterApp class from vapp.py
from vapp import SeatAdjusterApp  # type: ignore # noqa: E402


@pytest.mark.asyncio
async def test_on_seat_position_changed():
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    # Create a MagicMock instance to mock the value attribute
    position_data_point_value_mock = MagicMock(value=5)

    # Create a MagicMock instance to mock the data point
    position_data_point_mock = MagicMock()
    position_data_point_mock.get.return_value = position_data_point_value_mock

    # Create a MagicMock instance to mock the DataPointReply class
    position_data_point_reply_mock = MagicMock(spec=DataPointReply)
    position_data_point_reply_mock.return_value = position_data_point_mock

    # Mock the publish_event method
    seat_adjuster_app.publish_event = AsyncMock()

    # Call the method under test
    await seat_adjuster_app.on_seat_position_changed(position_data_point_reply_mock())

    # Assert that publish_event was called with the correct arguments

    # TODO check if MQTT message is published


@pytest.mark.asyncio
async def test_on_set_position_request_received_vehicle_not_moving():
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    vehicle_speed_data_point = TypedDataPointResult[float](
        "foo", 0, Timestamp(seconds=10, nanos=0)
    )

    request_data_str = get_valid_request_data_str()

    with mock.patch.object(
        vehicle.Speed,
        "get",
        new_callable=mock.AsyncMock,
        return_value=vehicle_speed_data_point,
    ):
        called_data_point = seat_adjuster_app.Vehicle.Cabin.Seat.Row1.Pos1.Position
        called_data_point.set = AsyncMock()
        seat_adjuster_app.publish_event = AsyncMock()

        await seat_adjuster_app.on_set_position_request_received(request_data_str)

        # TODO check if datapoint is set and MQTT message is published


@pytest.mark.asyncio
async def test_on_set_position_request_received_vehicle_moving():
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    vehicle_speed_data_point = TypedDataPointResult[float](
        "foo", 5, Timestamp(seconds=10, nanos=0)
    )

    request_data_str = get_valid_request_data_str()

    with mock.patch.object(
        vehicle.Speed,
        "get",
        new_callable=mock.AsyncMock,
        return_value=vehicle_speed_data_point,
    ):
        seat_adjuster_app.publish_event = AsyncMock()

        await seat_adjuster_app.on_set_position_request_received(request_data_str)

        # TODO check if message is published


@pytest.mark.asyncio
async def test_on_set_position_request_received_error_path():
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    vehicle_speed_data_point = TypedDataPointResult[float](
        "foo", 0, Timestamp(seconds=10, nanos=0)
    )

    request_data_str = get_valid_request_data_str()

    with mock.patch.object(
        vehicle.Speed,
        "get",
        new_callable=mock.AsyncMock,
        return_value=vehicle_speed_data_point,
    ):
        called_data_point = seat_adjuster_app.Vehicle.Cabin.Seat.Row1.Pos1.Position
        called_data_point.set = AsyncMock(side_effect=async_raise_exception)
        seat_adjuster_app.publish_event = AsyncMock()

        await seat_adjuster_app.on_set_position_request_received(request_data_str)

        # TODO check if datapoint is set and MQTT message is published


@pytest.mark.asyncio
async def test_on_set_position_request_received_high_position():
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    vehicle_speed_data_point = TypedDataPointResult[float](
        "foo", 0, Timestamp(seconds=10, nanos=0)
    )

    request_data_str = get_invalid_request_data_str()

    with mock.patch.object(
        vehicle.Speed,
        "get",
        new_callable=mock.AsyncMock,
        return_value=vehicle_speed_data_point,
    ):
        called_data_point = seat_adjuster_app.Vehicle.Cabin.Seat.Row1.Pos1.Position
        called_data_point.set = AsyncMock(side_effect=async_raise_value_error)
        seat_adjuster_app.publish_event = AsyncMock()

        await seat_adjuster_app.on_set_position_request_received(request_data_str)

        # TODO check if datapoint is set and MQTT message is published


def get_valid_request_data_str():
    return '{"requestId": 123, "position": 10}'


def get_invalid_request_data_str():
    return '{"requestId": 123, "position": 1001}'


async def async_raise_exception(*args):
    raise Exception("Unknown error")


async def async_raise_value_error(*args):
    data = json.loads(get_invalid_request_data_str())
    raise ValueError(
        f"""Provided position {data['position']}  \
        should not be Greater than 1000 (Max)"""
    )
