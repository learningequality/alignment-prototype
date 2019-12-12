##################################################
# MIT License
#
# Copyright (c) 2019 Learning Equality
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
##################################################

from datetime import datetime
import os
import numpy as np
import pandas as pd
import random
import scipy.stats

from django.conf import settings

from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment

TEST_DATA_DUMP_PATH = os.path.join(settings.DATA_EXPORT_BASE_DIR, "../testdata")


def ranking(model):
    judgments = pd.read_csv(
        os.path.join(TEST_DATA_DUMP_PATH, "humanjudgments.csv"), index_col="id"
    ).fillna("")
    judgments_test = pd.read_csv(
        os.path.join(TEST_DATA_DUMP_PATH, "humanjudgments_test.csv"), index_col="id"
    ).fillna("")

    return {
        "training": ranking_for_judgments(model, judgments),
        "testing": ranking_for_judgments(model, judgments_test),
    }


def get_rank(row, item):
    percentile = scipy.stats.percentileofscore(row, item) / 100
    return (1 - percentile) * len(row)


def ranking_for_judgments(model, judgments):
    """
    """

    modeldirpath = os.path.join(settings.MODELS_BASE_DIR, model)
    baselinemodeldirpath = os.path.join(settings.MODELS_BASE_DIR, "baseline")

    # load the index
    # node_id_lookup = np.load(os.path.join(modeldirpath, "index.npy"))
    node_id_lookup = np.load(os.path.join(modeldirpath, "index.npy"))

    # load the matrix
    # relevance_matrix = np.load(os.path.join(modeldirpath, "relevance.npy"))

    embeddings = np.load(os.path.join(modeldirpath, "embeddings.npy"))
    relevance_matrix = np.inner(embeddings, embeddings)

    # load the pickled DataFrame of nodes
    nodes = pd.read_pickle(os.path.join(baselinemodeldirpath, "nodes.pk"))

    percentiles_negative = []
    percentiles_moderate = []
    percentiles_positive = []
    for index in judgments.index:
        judgment = judgments.loc[index]
        prediction_row = relevance_matrix[judgment.node1_id, :].flatten()
        predicted_value = prediction_row[judgment.node2_id]
        percentile = scipy.stats.percentileofscore(prediction_row, predicted_value)
        if judgment.rating == 0.0:
            percentiles_negative.append(percentile)
        if judgment.rating == 0.5:
            percentiles_moderate.append(percentile)
        if judgment.rating == 1.0:
            percentiles_positive.append(percentile)

    # alternative:
    # loop over nodes: sort by model rating, then look at how "unsorted" the positives vs negatives are
    # (num nodes above above the lowest ranked positive not known to be positive)

    worst_ranks = []
    best_ranks = []

    i = 0
    for id, node in nodes.iterrows():
        i += 1
        if i % 1000 == 0:
            print("Working on node", i)
        prediction_row = relevance_matrix[node.row, :].flatten()
        matching_judgments = judgments[
            ((judgments.node1_id == id) | (judgments.node2_id == id))
            & (judgments.rating == 1)
        ]
        if matching_judgments.empty:
            continue
        node_ids = list(
            set(matching_judgments.node1_id)
            | set(matching_judgments.node2_id) - set([id])
        )
        node_predictions = prediction_row[nodes.loc[node_ids].row]
        worst_prediction = min(node_predictions)
        best_prediction = max(node_predictions)
        worst_rank = get_rank(prediction_row, worst_prediction) - len(node_ids) + 1
        best_rank = get_rank(prediction_row, best_prediction)

        worst_ranks.append(worst_rank)
        best_ranks.append(best_rank)

        # import IPython

        # IPython.embed()

    return {
        "avg_percentiles_negative": np.mean(percentiles_negative),
        "avg_percentiles_moderate": np.mean(percentiles_moderate),
        "avg_percentiles_positive": np.mean(percentiles_positive),
        "mean_best_rank": np.mean(best_ranks),
        "mean_worst_rank": np.mean(worst_ranks),
    }
