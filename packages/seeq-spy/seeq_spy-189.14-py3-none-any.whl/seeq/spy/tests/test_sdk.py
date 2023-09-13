import time

import pytest
from pandas import DataFrame
from seeq import spy
from seeq.sdk import SignalsApi, GetSamplesOutputV1
from seeq.spy import search
from seeq.spy.tests import test_common


def setup_module():
    test_common.log_in_default_user()
    test_common.wait_for_example_data(spy.session)


@pytest.mark.system
def test_get_signals_json():
    signal = search(DataFrame.from_dict({'Name': ['Area A_Temperature'], 'Type': ['StoredSignal']}), quiet=True).iloc[0]
    begin = time.time()
    response = SignalsApi(spy.session.client).get_samples(id=signal['ID'],
                                                          start='2022-01-01T00:00:00Z',
                                                          end='2022-01-30T00:00:00Z',
                                                          limit=10000,
                                                          _response_type="json")
    print(f"\nget_samples_json took {(time.time() - begin) * 1000} millis")
    assert isinstance(response, dict)
    assert 'samples' in response
    assert isinstance(response['samples'], list)
    assert len(response['samples']) == 10000


@pytest.mark.system
def test_get_signals_default():
    signal = search(DataFrame.from_dict({'Name': ['Area A_Temperature'], 'Type': ['StoredSignal']}), quiet=True).iloc[0]
    begin = time.time()
    response = SignalsApi(spy.session.client).get_samples(id=signal['ID'],
                                                          start='2022-01-01T00:00:00Z',
                                                          end='2022-01-30T00:00:00Z',
                                                          limit=10000)
    print(f"\nget_samples_default took {(time.time() - begin) * 1000} millis")
    assert isinstance(response, GetSamplesOutputV1)
    assert len(response.samples) == 10000
