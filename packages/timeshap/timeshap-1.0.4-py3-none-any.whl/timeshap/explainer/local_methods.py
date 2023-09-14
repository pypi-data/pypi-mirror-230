#  Copyright 2022 Feedzai
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Callable, Union, List, Tuple
import numpy as np
import pandas as pd
from timeshap.plot import plot_local_report
from timeshap.explainer import local_pruning, local_event, local_feat, local_cell_level
from timeshap.utils import validate_input


def validate_local_input(f: Callable[[np.ndarray], np.ndarray],
                         data: np.array,
                         pruning_dict: dict,
                         event_dict: dict,
                         feature_dict: dict,
                         cell_dict: dict = None,
                         baseline: Union[pd.DataFrame, np.ndarray]=None,
                         model_features: List[Union[int, str]] = None,
                         entity_col: Union[str, int] = None,
                         time_col: Union[str, int] = None,
                         entity_uuid: str = None,
                         ):
    """Verifies for local inputs if inputs are according

    Parameters
    ----------
    f: Callable[[np.ndarray], np.ndarray]
        Point of entry for model being explained.
        This method receives a 3-D np.ndarray (#samples, #seq_len, #features).
        This method returns a 2-D np.ndarray (#samples, 1).

    data: np.array
        Sequences to be explained.
        Must contain columns with names disclosed on `model_features`.

    pruning_dict: dict
        Information required for the pruning algorithm

    event_dict: dict
        Information required for the event level explanation calculation

    feature_dict: dict
        Information required for the feature level explanation calculation

    model_features: List[str]
        Features to be used by the model. Requires same order as training dataset

    entity_col: str
        Entity column to identify sequences

    time_col: str
        Data column that represents the time feature in order to sort sequences
        temporally
    """
    def check_dict(dict_to_check, key, types, message):
        if dict_to_check.get(key):
            assert isinstance(dict_to_check.get(key), types), message

    validate_input(f, data, baseline, model_features, None, entity_col, time_col)

    if isinstance(data, pd.DataFrame):
        data_cols = set(data.columns)
        if model_features:
            assert set(model_features).issubset(data_cols), "When providing model features, these should be on the given DataFrame"
        else:
            print("Assuming all features are model features")
            assert entity_col is None, "Entity col provided but no model features provided"
            assert time_col is None, "Time col provided but no model features provided"
        if entity_col is not None:
            assert entity_col in data_cols, "When providing entity feature, these should be on the given DataFrame"
            assert len(np.unique(data[entity_col].values)) == 1, "For local report, provided data must contain one instance only"
        if time_col is not None:
            assert time_col in data_cols, "When providing time feature, these should be on the given DataFrame"
    else:
        assert len(data.shape) == 3, "Provided data must be an numpy array with 3 dimensions"
        assert data.shape[0] == 1, "For local report, provided data must contain one instance only"

    assert baseline is None or isinstance(baseline, (pd.DataFrame, np.ndarray)), "Baseline must be a pd.DataFrame or np.ndarrays"

    assert pruning_dict is None or pruning_dict.get("tol") is not None, "Prunning dict must have tolerance attribute"
    if pruning_dict is not None:
        assert isinstance(pruning_dict.get("tol"), (int, float)), "Provided tolerance must be a int or float"
        if isinstance(pruning_dict.get("tol"), int):
            assert pruning_dict.get("tol") == 0, "Provided tolerance must be a float or 0"

    check_dict(event_dict, 'rs', int, "Provided random seed must be a int")
    check_dict(event_dict, 'nsamples', int, "Provided nsamples must be a int")
    check_dict(feature_dict, 'rs', int, "Provided random seed must be a int")
    check_dict(feature_dict, 'nsamples', int, "Provided nsamples must be a int")
    check_dict(feature_dict, 'top_feats', int, "Provided top_feats must be a int")
    check_dict(feature_dict, 'plot_features', dict, "Provided plot_features must be a dict, mapping model features, to plot features")

    if cell_dict is not None:
        check_dict(cell_dict, 'rs', int, "Provided random seed must be a int")
        check_dict(cell_dict, 'nsamples', int, "Provided nsamples must be a int")

        # assert we have
        if 'threshold' in cell_dict or 'top_x' in cell_dict:
            provided = 'threshold' if 'threshold' in cell_dict else 'top_x'
            assert 'feat_threshold' not in cell_dict, f"Provided both feat_threshold and {provided}. Please only provide one"
            assert 'top_x_feats' not in cell_dict, f"Provided both top_x_feats and {provided}. Please only provide one"
            assert 'event_threshold' not in cell_dict, f"Provided both event_threshold and {provided}. Please only provide one"
            assert 'top_x_events' not in cell_dict, f"Provided both top_x_events and {provided}. Please only provide one"
        else:
            if not('feat_threshold' in cell_dict or 'top_x_feats' in cell_dict):
                raise ValueError("No way to determine relevant features for cell level")

            if not ('event_threshold' in cell_dict or 'top_x_events' in cell_dict):
                raise ValueError( "No way to determine relevant events for cell level")


def calc_local_report(f: Callable[[np.ndarray], np.ndarray],
                      data: Union[pd.DataFrame, np.array],
                      pruning_dict: dict,
                      event_dict: dict,
                      feature_dict: dict,
                      cell_dict: dict = None,
                      baseline: Union[pd.DataFrame, np.ndarray] = None,
                      model_features: List[Union[int, str]] = None,
                      entity_col=None,
                      entity_uuid=None,
                      time_col=None,
                      verbose=False,
                      ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calculates local explanations

    Parameters
    ----------
    f: Callable[[np.ndarray], np.ndarray]
        Point of entry for model being explained.
        This method receives a 3-D np.ndarray (#samples, #seq_len, #features).
        This method returns a 2-D np.ndarray (#samples, 1).

    data: Union[pd.DataFrame, np.array]
        Sequence to be explained.

    pruning_dict: dict
        Information required for pruning algorithm

    event_dict: dict
        Information required for the event level explanation calculation

    feature_dict: dict
        Information required for the feature level explanation calculation

    cell_dict: dict
        Information required for the cell level explanation calculation

    entity_uuid: Union[str, int, float]
        The indentifier of the sequence that is being pruned.
        Used when fetching information from a csv of explanations

    entity_col: str
        Entity column to identify sequences

    time_col: str
        Data column that represents the time feature in order to sort sequences
        temporally

    model_features: List[str]
        Features to be used by the model. Requires same order as training dataset

    baseline: Union[pd.DataFrame, np.array]
        Dataset baseline. Median/Mean of numerical features and mode of categorical.
        In case of np.array feature are assumed to be in order with `model_features`.

    verbose: bool
        If process is verbose

    Returns
    -------
    pd.DataFrame
        Local pruning algorithm data

    pd.DataFrame
        Local event explanations

    pd.DataFrame
        Local feature explanations

    pd.DataFrame
        Local cell explanations
    """
    validate_local_input(f, data, pruning_dict, event_dict, feature_dict, cell_dict,
                         baseline, model_features, entity_col, time_col, entity_uuid)
    # deals with given date being a DataFrame
    if isinstance(data, pd.DataFrame):
        if time_col is not None:
            data[time_col] = data[[time_col]].apply(pd.to_numeric)
            data = data.sort_values(time_col)
        if model_features is not None:
            data = data[model_features]
        else:
            data = data.values
        data = np.expand_dims(data.to_numpy().copy(), axis=0).astype(float)

    if pruning_dict is None:
        print("No pruning dict passed. Skipping pruning procedures")
        pruning_idx = 0
        coal_plot_data = None
    else:
        coal_plot_data, coal_prun_idx = local_pruning(f, data, pruning_dict, baseline, entity_uuid, entity_col, verbose)
        pruning_idx = data.shape[1] + coal_prun_idx

    event_data = local_event(f, data, event_dict, entity_uuid, entity_col, baseline, pruning_idx)

    feature_data = local_feat(f, data, feature_dict, entity_uuid, entity_col, baseline, pruning_idx)

    if cell_dict:
        cell_data = local_cell_level(f, data, cell_dict, event_data, feature_data, entity_uuid, entity_col, baseline, pruning_idx)
    else:
        cell_data = None

    return coal_plot_data, event_data, feature_data, cell_data


def local_report(f: Callable[[np.ndarray], np.ndarray],
                 data: Union[pd.DataFrame, np.array],
                 pruning_dict: dict,
                 event_dict: dict,
                 feature_dict: dict,
                 cell_dict: dict = None,
                 baseline: Union[pd.DataFrame, np.array] = None,
                 model_features: List[Union[str, int]] = None,
                 entity_col: str = None,
                 entity_uuid: str = None,
                 time_col: str = None,
                 verbose=False,
                 ):
    """Calculates local report and plots it.

     `None` on the pruning_dict argument makes TimeSHAP skip the pruning step.

    Parameters
    ----------
    f: Callable[[np.ndarray], np.ndarray]
        Point of entry for model being explained.
        This method receives a 3-D np.ndarray (#samples, #seq_len, #features).
        This method returns a 2-D np.ndarray (#samples, 1).

    data: Union[pd.DataFrame, np.array]
        Sequence to be explained.

    pruning_dict: dict
        Information required for pruning algorithm

    event_dict: dict
        Information required for the event level explanation calculation

    feature_dict: dict
        Information required for the feature level explanation calculation

    cell_dict: dict
        Information required for the cell level explanation calculation

    entity_uuid: Union[str, int, float]
        The indentifier of the sequence that is being pruned.
        Used when fetching information from a csv of explanations

    entity_col: str
        Entity column to identify sequences

    time_col: str
        Data column that represents the time feature in order to sort sequences
        temporally

    model_features: List[str]
        Features to be used by the model. Requires same order as training dataset

    baseline: Union[pd.DataFrame, np.array]
        Dataset baseline. Median/Mean of numerical features and mode of categorical.
        In case of np.array feature are assumed to be in order with `model_features`.

    verbose: bool
        If process is verbose
    """
    pruning_data, event_data, feature_data, cell_level = \
        calc_local_report(f, data, pruning_dict, event_dict, feature_dict,
                          cell_dict, baseline, model_features, entity_col,
                          entity_uuid, time_col, verbose
                          )
    plot = plot_local_report(pruning_dict, event_dict, feature_dict, cell_dict,
                             pruning_data, event_data, feature_data, cell_level
                             )
    return plot
