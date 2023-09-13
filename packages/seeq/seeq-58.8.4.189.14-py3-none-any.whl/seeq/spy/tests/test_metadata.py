import cProfile
import io
import json
import math
import os
import pstats
import tempfile

import numpy as np
import pandas as pd
import pytest
from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _metadata
from seeq.spy._errors import *
from seeq.spy.tests import test_common


def setup_module():
    test_common.initialize_sessions()


def assert_datasource_properties(datasource_output, name, datasource_class, datasource_id,
                                 expected_additional_properties):
    assert datasource_output.datasource_class == datasource_class
    assert datasource_output.datasource_id == datasource_id
    assert datasource_output.name == name
    assert not datasource_output.is_archived
    assert datasource_output.stored_in_seeq
    assert not datasource_output.cache_enabled
    assert datasource_output.description == _common.DEFAULT_DATASOURCE_DESCRIPTION
    assert len(datasource_output.additional_properties) == expected_additional_properties
    filtered_properties = filter(lambda x: x.name == 'Expect Duplicates During Indexing',
                                 datasource_output.additional_properties)
    additional_property = list(filtered_properties)[0]
    assert additional_property.value


@pytest.mark.system
def test_create_datasource():
    datasources_api = DatasourcesApi(spy.session.client)

    with pytest.raises(ValueError):
        _metadata.create_datasource(spy.session, 1)

    _metadata.create_datasource(spy.session, 'test_datasource_name_1')

    datasource_output_list = datasources_api.get_datasources(limit=100000)  # type: DatasourceOutputListV1
    datasource_output = list(filter(lambda d: d.name == 'test_datasource_name_1',
                                    datasource_output_list.datasources))[0]  # type: DatasourceOutputV1

    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_1',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_name_1', 3)

    with pytest.raises(ValueError, match='"Datasource Name" required for datasource'):
        _metadata.create_datasource(spy.session, {
            'Blah': 'test_datasource_name_2'
        })

    datasource_output = _metadata.create_datasource(spy.session, {
        'Datasource Name': 'test_datasource_name_2'
    })
    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_2',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_name_2', 3)

    datasource_output = _metadata.create_datasource(spy.session, {
        'Datasource Name': 'test_datasource_name_3',
        'Datasource ID': 'test_datasource_id_3'
    })
    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_3',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_id_3', 3)

    with pytest.raises(ValueError):
        _metadata.create_datasource(spy.session, {
            'Datasource Class': 'test_datasource_class_4',
            'Datasource Name': 'test_datasource_name_4',
            'Datasource ID': 'test_datasource_id_4'
        })


@pytest.mark.system
def test_crab_25450():
    # This was a nasty bug. In the case where the user had a "Scoped To" column in their metadata DataFrame [possibly
    # as a result of creating it via spy.search(all_properties=True)], then _metadata.get_scoped_data_id() would
    # assign all items to global scope. The top of the asset tree would be locally scoped because it's treated
    # differently in _metadata._reify_path().
    #
    # _metadata.get_scoped_data_id() has been fixed so that it always sets a scope that is consistent with the Data
    # ID it is constructing. However, plenty of metadata has been pushed with the old bug in place, and we don't want
    # to cause a big headache of 'Attempted to set scope on a globally scoped item' errors coming back from Appserver
    # (read CRAB-25450 for more info).
    #
    # This test recreates the problem and then ensures the problem is handled by the code that detects the situation and
    # accommodates existing trees that have the problem.
    search_df = spy.search({'Name': 'Area E_Temperature'},
                           workbook=spy.GLOBALS_ONLY)

    # The key to reproducing the problem is including a 'Scoped To' column that is blank
    metadata_df = pd.DataFrame([
        {
            'Name': 'test_CRAB_25450 Asset',
            'Type': 'Asset',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Signal',
            'Type': 'Signal',
            'Formula': 'sinusoid()',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Condition',
            'Type': 'Condition',
            'Formula': 'weeks()',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Scalar',
            'Type': 'Scalar',
            'Formula': '1',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Type': 'Threshold Metric',
            'Name': 'push test threshold metric',
            'Measured Item': search_df.iloc[0]['ID'],
        }
    ])
    workbook = 'test_crab_25450'
    push_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    assert len(push_df) == 6  # Not 5 because it will include the (implicitly-specified) top level asset

    items_api = ItemsApi(spy.client)
    assets_api = AssetsApi(spy.client)
    signals_api = SignalsApi(spy.client)
    conditions_api = ConditionsApi(spy.client)
    scalars_api = ScalarsApi(spy.client)
    metrics_api = MetricsApi(spy.client)

    for index, row in push_df.iterrows():
        # This recreates the bug by manually setting all the pushed items to global scope
        items_api.set_scope(id=row['ID'])

    def _get_outputs(_df):
        return (assets_api.get_asset(id=_df.iloc[0]['ID']),
                signals_api.get_signal(id=_df.iloc[1]['ID']),
                conditions_api.get_condition(id=_df.iloc[2]['ID']),
                scalars_api.get_scalar(id=_df.iloc[3]['ID']),
                metrics_api.get_metric(id=_df.iloc[4]['ID']))

    outputs = _get_outputs(push_df)

    for output in outputs:
        assert output.scoped_to is None

    # This will succeed due to our code to handle the situation.
    push2_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    for i in range(0, 5):
        assert push_df.iloc[i]['ID'] == push2_df.iloc[i]['ID']

    outputs = _get_outputs(push2_df)

    # The scope will still be wrong, but there's nothing we can do about it
    for output in outputs:
        assert output.scoped_to is None

    # Now push to a different workbook (without the recreation flag enabled)
    push3_df = spy.push(metadata=metadata_df, workbook=f'{workbook} - Corrected', worksheet=None, datasource=workbook)

    # Should be different items
    for i in range(0, 5):
        assert push_df.iloc[i]['ID'] != push3_df.iloc[i]['ID']

    outputs = _get_outputs(push3_df)

    # The scope will be correct
    for output in outputs:
        assert output.scoped_to is not None


@pytest.mark.system
def test_crab_25450_2():
    # In addition to the use case above, there is also a case where signals/conditions that are (implicitly) created
    # as part of a spy.push(data=df) can become globally scoped, and then it's not possible to push them again. Once
    # we fixed CRAB-25450, users started running into this. See SUP-41382.
    workbook = 'test_crab_25450_2'

    items_api = ItemsApi(spy.client)

    def _globally_scope(_items):
        for _item_id in _items['ID'].to_list():
            items_api.set_scope(id=_item_id)

    signal_data = pd.DataFrame(index=[
        pd.to_datetime('2019-01-01', utc=True),
        pd.to_datetime('2019-01-02', utc=True),
        pd.to_datetime('2019-01-03', utc=True),
        pd.to_datetime('2019-01-04', utc=True)
    ])
    signal_data['My Signal'] = [10, 20, 30, 40]

    signal_push_df = spy.push(signal_data, workbook=workbook, worksheet=None, datasource=workbook)

    _globally_scope(signal_push_df)
    signal_data['My Signal'] = [1, 2, 3, 4]
    signal_push_df = spy.push(signal_data, workbook=workbook, worksheet=None, datasource=workbook)

    condition_data = pd.DataFrame([{
        'Capsule Start': pd.to_datetime('2018-01-01', utc=True),
        'Capsule End': pd.to_datetime('2018-01-02', utc=True),
    }, {
        'Capsule Start': pd.to_datetime('2018-01-03', utc=True),
        'Capsule End': pd.to_datetime('2018-01-04', utc=True),
    }])
    condition_metadata = pd.DataFrame([{
        'Name': 'My Condition',
        'Type': 'Condition',
        'Maximum Duration': '2 days'
    }])

    condition_push_df = spy.push(condition_data, metadata=condition_metadata, workbook=workbook,
                                 worksheet=None, datasource=workbook)

    _globally_scope(condition_push_df)
    condition_data = pd.DataFrame([{
        'Capsule Start': pd.to_datetime('2019-01-01', utc=True),
        'Capsule End': pd.to_datetime('2019-01-02', utc=True),
    }, {
        'Capsule Start': pd.to_datetime('2019-01-03', utc=True),
        'Capsule End': pd.to_datetime('2019-01-04', utc=True),
    }])
    condition_push_df = spy.push(condition_data, metadata=condition_metadata, workbook=workbook,
                                 worksheet=None, datasource=workbook)

    pull_signal_df1 = spy.pull(signal_push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z', grid=None)

    test_common.make_index_naive(pull_signal_df1)

    assert len(pull_signal_df1) == 4
    assert pull_signal_df1.at[pd.to_datetime('2019-01-01'), 'My Signal'] == 1
    assert pull_signal_df1.at[pd.to_datetime('2019-01-02'), 'My Signal'] == 2
    assert pull_signal_df1.at[pd.to_datetime('2019-01-03'), 'My Signal'] == 3
    assert pull_signal_df1.at[pd.to_datetime('2019-01-04'), 'My Signal'] == 4

    pull_condition_df1 = spy.pull(condition_push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z',
                                  grid=None)

    assert len(pull_condition_df1) == 2
    assert pull_condition_df1.at[0, 'Capsule Start'] == pd.to_datetime('2019-01-01', utc=True)
    assert pull_condition_df1.at[0, 'Capsule End'] == pd.to_datetime('2019-01-02', utc=True)
    assert pull_condition_df1.at[1, 'Capsule Start'] == pd.to_datetime('2019-01-03', utc=True)
    assert pull_condition_df1.at[1, 'Capsule End'] == pd.to_datetime('2019-01-04', utc=True)


@pytest.mark.system
def test_bad_formula_error_message():
    search_df = spy.search({'Name': 'Area B_Temperature'},
                           workbook=spy.GLOBALS_ONLY)
    temperature_id = search_df.iloc[0]['ID']

    search_df = spy.search({'Name': 'Area B_Compressor Power'},
                           workbook=spy.GLOBALS_ONLY)
    power_id = search_df.iloc[0]['ID']

    conditions_api = ConditionsApi(spy.session.client)

    condition_input = ConditionInputV1(
        name='test_bad_formula',
        formula='$power > 20 kW and $temp < 60 Faq',
        parameters=[
            f'power={power_id}',
            f'temp={temperature_id}'
        ],
        datasource_id=_common.DEFAULT_DATASOURCE_ID,
        datasource_class=_common.DEFAULT_DATASOURCE_CLASS
    )
    condition_update_input = ConditionUpdateInputV1(
        name=condition_input.name,
        formula=condition_input.formula,
        parameters=condition_input.parameters,
        datasource_id=condition_input.datasource_id,
        datasource_class=condition_input.datasource_class,
        replace_capsule_properties=True
    )

    expected_error = 'Unknown unit of measure \'Faq\' at \'Faq\', line=1, column=31'
    error_message = None
    try:
        conditions_api.create_condition(body=condition_input)
    except ApiException as e:
        error_message = json.loads(e.body)['statusMessage']

    assert expected_error in error_message

    item_batch_output = conditions_api.put_conditions(body=ConditionBatchInputV1(
        conditions=[condition_update_input]
    ))

    error_message = item_batch_output.item_updates[0].error_message

    assert expected_error in error_message


@pytest.mark.system
def test_metadata_dataframe_weird_index():
    workbook = 'test_metadata_dataframe_weird_index'

    metadata_df = pd.DataFrame({
        'Type': ['Signal', 'Signal'],
        'Name': [f'{workbook}1', f'{workbook}2'],
        'Path': workbook,
        'Asset': ['Asset 1', 'Asset 2'],
        'Formula': ['sinusoid()', 'sawtooth()']
    },
        # An index of 3, 4 here will replicate the scenario -- if _metadata.py doesn't reset the index for the
        # push_result_df, it will be messed up because the wrong rows will be overwritten for the Push Result column.
        index=pd.Index([3, 4], name='Hey!')
    )

    push_result_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    # Three Asset entries will be added to the end of the resulting DataFrame with nan index entries
    assert push_result_df.index.equals(pd.Index([3.0, 4.0, np.nan, np.nan, np.nan]))
    assert push_result_df.index.name == 'Hey!'


@pytest.mark.system
def test_incremental_metadata_push():
    workbook = 'test_incremental_metadata_push'
    metadata = pd.DataFrame([{
        'Type': 'Metric',
        'Name': 'My Metric',
        'Asset': 'Asset 1',
        'Path': workbook,
        'Measured Item': {'Name': 'My Signal', 'Asset': 'Asset 1', 'Path': workbook}
    }, {
        'Type': 'Condition',
        'Name': 'My Condition',
        'Asset': 'Asset 1',
        'Path': workbook,
        'Formula': '$s > $c',
        'Formula Parameters': {
            '$s': {'Name': 'My Signal', 'Asset': 'Asset 1', 'Path': workbook},
            '$c': {'Name': 'My Scalar', 'Asset': 'Asset 1', 'Path': workbook}
        }
    }, {
        'Type': 'Signal',
        'Name': 'My Signal',
        'Asset': 'Asset 1',
        'Path': workbook,
        'Formula': 'sinusoid(10min)'
    }, {
        'Type': 'Scalar',
        'Name': 'My Scalar',
        'Asset': 'Asset 1',
        'Path': workbook,
        'Formula': '5'
    }, {
        'Type': 'Asset',
        'Name': 'Asset 2',
        'Asset': 'Asset 2',
        'Path': workbook
    }, {
        'Type': 'Scalar',
        'Name': 'Scalar to Drop',
        'Asset': 'Asset 1',
        'Path': workbook,
        'Formula': '15'
    }])

    expected_length = len(metadata) + 2

    with tempfile.TemporaryDirectory() as temp_dir:
        pickle_file_name = os.path.join(temp_dir, f'{workbook}.pickle.zip')

        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        assert len(push_results_df) == expected_length
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success']

        # No changes
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        assert len(push_results_df) == expected_length
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Add an item
        my_other_scalar_row_index = len(metadata)
        metadata.loc[my_other_scalar_row_index] = {
            'Type': 'Scalar',
            'Name': 'My Other Scalar',
            'Asset': 'Asset 1',
            'Path': workbook,
            'Formula': '10'
        }
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        expected_length += 1
        assert len(push_results_df) == expected_length
        my_other_scalar_row = push_results_df.loc[my_other_scalar_row_index]
        assert my_other_scalar_row['Push Result'] == 'Success'
        push_results_df.drop(my_other_scalar_row_index, inplace=True)
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Cause an error and make sure the correction can be pushed
        metadata.at[1, 'Formula'] = 'this will not work'
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name, errors='catalog')
        assert len(push_results_df) == expected_length
        my_condition = push_results_df.loc[1]
        assert my_condition['Push Result'].startswith('Failed to write')
        push_results_df.drop(1, inplace=True)
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Correct the error (we'll verify it at the end)
        metadata.at[1, 'Formula'] = '$s < $c + 100'

        # Change a formula parameter on a condition
        metadata.at[1, 'Formula Parameters'] = {
            '$s': {'Name': 'My Signal', 'Asset': 'Asset 1', 'Path': workbook},
            '$c': {'Name': 'My Other Scalar', 'Asset': 'Asset 1', 'Path': workbook}
        }
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        assert len(push_results_df) == expected_length
        my_condition = push_results_df.loc[1]
        assert my_condition['Push Result'] == 'Success'
        push_results_df.drop(1, inplace=True)
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Change a parameter on a metric
        metadata.at[0, 'Measured Item'] = {'Name': 'My Condition', 'Asset': 'Asset 1', 'Path': workbook}
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        assert len(push_results_df) == expected_length
        my_metric = push_results_df.loc[0]
        assert my_metric['Push Result'] == 'Success'
        push_results_df.drop(0, inplace=True)
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Change a path
        metadata.at[3, 'Asset'] = 'Asset 2'
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name)
        assert len(push_results_df) == expected_length
        my_signal = push_results_df.loc[3]
        assert my_signal['Push Result'] == 'Success'
        push_results_df.drop(3, inplace=True)
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

        # Drop an item
        metadata.drop(5, inplace=True)
        push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                                   metadata_state_file=pickle_file_name, archive=True)
        expected_length -= 1
        assert len(push_results_df) == expected_length
        assert push_results_df['Push Result'].drop_duplicates().to_list() == ['Success: Unchanged']

    search_df = spy.search({'Path': workbook}, workbook=workbook, recursive=True, all_properties=True,
                           old_asset_format=True)
    assert len(search_df) == 7
    search_df = search_df[['ID', 'Type', 'Path', 'Asset', 'Name', 'Formula', 'Formula Parameters', 'Measured Item']]
    my_metric = search_df[search_df['Name'] == 'My Metric'].iloc[0]
    my_condition = search_df[search_df['Name'] == 'My Condition'].iloc[0]
    my_signal = search_df[search_df['Name'] == 'My Signal'].iloc[0]
    assert len(search_df[search_df['Name'] == 'My Scalar']) == 1
    my_scalar = search_df[search_df['Name'] == 'My Scalar'].iloc[0]
    asset_2 = search_df[search_df['Name'] == 'Asset 2'].iloc[0]
    my_other_scalar = search_df[search_df['Name'] == 'My Other Scalar'].iloc[0]
    assert len(search_df[search_df['Name'] == 'Scalar to Drop']) == 0

    assert my_condition['Formula'] == '$s < $c + 100'
    assert sorted(my_condition['Formula Parameters']) == sorted([f's={my_signal["ID"]}', f'c={my_other_scalar["ID"]}'])
    assert my_metric['Measured Item'] == my_condition['ID']
    assert my_scalar['Asset'] == 'Asset 2'
    assert asset_2['Asset'] == workbook
    assert my_other_scalar['Formula'] == '10'


@pytest.mark.system
def test_push_directives_create_and_update_only():
    workbook = 'test_push_directives_create_and_update_only'
    _test_push_directives_create_and_update_only(None, workbook)


@pytest.mark.system
def test_push_directives_create_and_update_only_incremental():
    workbook = 'test_push_directives_create_and_update_only_incremental'
    with tempfile.TemporaryDirectory() as temp_dir:
        pickle_file_name = os.path.join(temp_dir, f'test_push_directives_create_and_update_only.pickle.zip')
        _test_push_directives_create_and_update_only(pickle_file_name, workbook)


def _test_push_directives_create_and_update_only(metadata_state_file, workbook):
    metadata = pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'My Signal ' + _common.new_placeholder_guid(),
        'Formula': 'sinusoid(400min)',
        'Push Directives': 1
    }])

    with pytest.raises(SPyTypeError):
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=metadata_state_file)

    metadata['Push Directives'] = 'Bogus'
    with pytest.raises(SPyValueError, match='not recognized'):
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=metadata_state_file)

    metadata['Push Directives'] = 'CreateOnly;UpdateOnly'
    with pytest.raises(SPyValueError, match='mutually exclusive'):
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=metadata_state_file)

    metadata['Push Directives'] = 'UpdateOnly'
    push_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                       metadata_state_file=metadata_state_file)
    assert push_df.iloc[0]['Push Result'] == 'Success: Skipped due to UpdateOnly push directive -- item does not exist'

    metadata['Push Directives'] = 'CreateOnly'
    push_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                       metadata_state_file=metadata_state_file)
    assert push_df.iloc[0]['Push Result'] == 'Success'

    push_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                       metadata_state_file=metadata_state_file)
    assert push_df.iloc[0]['Push Result'] == 'Success: Skipped due to CreateOnly push directive -- item already exists'

    metadata['Push Directives'] = 'UpdateOnly'
    metadata['Formula'] = 'sawtooth(100s)'
    push_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                       metadata_state_file=metadata_state_file)
    assert push_df.iloc[0]['Push Result'] == 'Success'

    # Make sure an item doesn't get archived just because it is skipped
    metadata['Push Directives'] = 'CreateOnly'
    push_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None, archive=True,
                       metadata_state_file=metadata_state_file)

    search_df = spy.search({'ID': push_df.iloc[0]['ID']}, all_properties=True)
    assert len(search_df) == 1
    assert search_df.iloc[0]['Formula'] == 'sawtooth(100s)'
    assert 'Push Directives' not in search_df.columns


@pytest.mark.performance
def test_metadata_incremental_push_performance():
    workbook = 'test_metadata_incremental_push_performance'
    count = 100000
    metadata = pd.DataFrame({
        'Name': [f'Signal ' + str(i).zfill(math.floor(math.log(count, 10))) for i in range(count)],
        'Type': 'Signal',
        'Formula': [f'sinusoid({i + 1}s)' for i in range(count)]
    })

    with tempfile.TemporaryDirectory() as temp_dir:
        pickle_file_name = os.path.join(temp_dir, f'{workbook}.pickle.zip')
        timer = _common.timer_start()
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=pickle_file_name)
        print(f'Initial push of {count} items took {int(_common.timer_elapsed(timer).total_seconds() * 1000)} ms')

        timer = _common.timer_start()
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=pickle_file_name)
        print(f'Second push of {count} with no changes {int(_common.timer_elapsed(timer).total_seconds() * 1000)} ms')

        metadata.iloc[0]['Formula'] = 'sawtooth(15min)'
        timer = _common.timer_start()
        spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None,
                 metadata_state_file=pickle_file_name)
        print(f'Third push of {count} with one change {int(_common.timer_elapsed(timer).total_seconds() * 1000)} ms')


@pytest.mark.performance
def test_metadata_push_performance_flat_tags():
    workbook = 'test_metadata_push_performance_flat_tags'
    count = 200000
    metadata = pd.DataFrame({
        'Name': [f'Signal ' + str(i).zfill(math.floor(math.log(count, 10))) for i in range(count)],
        'Type': 'Signal',
        'Formula': [f'sinusoid({i + 1}s)' for i in range(count)]
    })

    timer = _common.timer_start()
    pr = cProfile.Profile()
    pr.enable()

    spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None)

    pr.disable()
    s = io.StringIO()
    sort_by = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sort_by)
    ps.print_stats()
    print(s.getvalue())

    print(f'Push of {count} items took {int(_common.timer_elapsed(timer).total_seconds() * 1000)} ms')


@pytest.mark.performance
def test_metadata_push_performance_tree():
    workbook = 'test_metadata_push_performance_tree'
    count = 100000
    order = math.floor(math.log(count, 10))

    def _path(n):
        path_parts = list()
        for i in range(order - 1):
            modulo = int(math.pow(10, i + 1))
            section = n - int(n % modulo)
            path_parts.insert(0, f'Section {section}')

        return ' >> '.join(path_parts)

    metadata = pd.DataFrame({
        'Name': 'The Signal',
        'Asset': [f'Asset ' + str(i).zfill(order) for i in range(count)],
        'Path': [_path(i) for i in range(count)],
        'Type': 'Signal',
        'Formula': [f'sinusoid({i + 1}s)' for i in range(count)]
    })

    timer = _common.timer_start()
    pr = cProfile.Profile()
    pr.enable()

    push_results_df = spy.push(metadata=metadata, workbook=workbook, datasource=workbook, worksheet=None)

    pr.disable()
    s = io.StringIO()
    sort_by = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sort_by)
    ps.print_stats()
    print(s.getvalue())

    print(f'Push of {count} items took {int(_common.timer_elapsed(timer).total_seconds() * 1000)} ms')

    print(f'Length of DataFrame: {len(push_results_df)}')
