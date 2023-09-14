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
import pandas as pd
from timeshap.explainer import pruning_statistics
from timeshap.plot import plot_global_feat, plot_global_event
import altair as alt
from timeshap.plot import find_parameters_to_plot, filter_dataset


def plot_global_report(pruning_dict: dict,
                       event_dict: dict,
                       feature_dict: dict,
                       prun_indexes: pd.DataFrame = None,
                       event_data: pd.DataFrame = None,
                       feat_data: pd.DataFrame = None
                       ):
    """Plots global epxlanation plots

    Parameters
    ----------
    pruning_dict: dict
        Information required for the pruning algorithm

    event_dict: dict
        Information required for the event level explanation calculation

    feature_dict: dict
        Information required for the feature level explanation calculation

    prun_indexes: pd.DataFrame
        Global Pruning information

    event_data: pd.DataFrame
        Global event explanations to plot

    feat_data: pd.DataFrame
        Global feature explanations to plot
    """
    if pruning_dict is None:
        if pruning_dict is not None:
            assert pruning_dict.get('path', False), "No data or path to data provided to calculate pruning statistics"
    if event_data is None:
        assert event_dict.get('path', False), "No data or path to data provided to plot event explanations"
    if feat_data is None:
        assert feature_dict.get('path', False), "No data or path to data provided to plot feature explanations"

    if prun_indexes is None:
        if pruning_dict is not None and pruning_dict.get('path'):
            prun_indexes = pd.read_csv(pruning_dict.get('path'))
    if event_data is None:
        event_data = pd.read_csv(event_dict.get('path'))
    if feat_data is None:
        feat_data = pd.read_csv(feature_dict.get('path'))

    if pruning_dict is None:
        pruning_stats = None
    else:
        print("Calculating pruning indexes")
        pruning_stats = pruning_statistics(prun_indexes, pruning_dict.get('tol'))

    plot_tols, plot_rs, plot_nsamples = find_parameters_to_plot(event_dict, feature_dict, event_data, feat_data)

    final_plot = alt.vconcat()
    for tolerance in plot_tols:
        for rs in plot_rs:
            for nsamples in plot_nsamples:

                plot_event_data = filter_dataset(event_data, tolerance, rs, nsamples)
                event_global_plot = plot_global_event(plot_event_data)

                plot_feat_data = filter_dataset(feat_data, tolerance, rs, nsamples)
                feat_global_plot = plot_global_feat(plot_feat_data, **feature_dict)

                horizontal_plot = alt.hconcat(event_global_plot, feat_global_plot, center=True)

                horizontal_plot = horizontal_plot.properties(
                    title=f"Parameters: NSamples={nsamples} | Random Seed={rs} | Pruning Tol= {tolerance}"
                )
                final_plot &= horizontal_plot

    return pruning_stats, final_plot
