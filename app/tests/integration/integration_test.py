# Copyright (c) 2022-2023 Robert Bosch GmbH and Microsoft Corporation
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

import pytest
from velocitas_sdk.test.inttesthelper import IntTestHelper
from velocitas_sdk.test.mqtt_util import MqttClient

REQUEST_TOPIC = "seatadjuster/setPosition/request"
RESPONSE_TOPIC = "seatadjuster/setPosition/response"


@pytest.mark.asyncio
async def test_set_position_not_allowed():
    mqtt_client = MqttClient()
    inttesthelper = IntTestHelper()
    request_id = 123

    payload = {"position": 300, "requestId": request_id}
    speed_value = 50
    response = await inttesthelper.set_float_datapoint(
        name="Vehicle.Speed", value=speed_value
    )

    assert len(response.errors) == 0

    response = mqtt_client.publish_and_wait_for_response(
        request_topic=REQUEST_TOPIC,
        response_topic=RESPONSE_TOPIC,
        payload=payload,
    )
    # TODO check response
