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

from django.conf import settings

from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


def recommend_top_ranked(queryset, target_node, threshold, count, model="baseline"):
    """
    """

    modeldirpath = os.path.join(settings.MODELS_BASE_DIR, model)

    # load the index
    node_id_lookup = np.load(os.path.join(modeldirpath, "index.npy"))

    # load the matrix
    relevance_matrix = np.load(os.path.join(modeldirpath, "relevance.npy"))

    # load the pickled DataFrame of nodes
    nodes = pd.read_pickle(os.path.join(modeldirpath, "nodes.pk"))

    # sanity checks
    n = len(node_id_lookup)
    assert relevance_matrix.shape[0] == n, "relevance_matrix has wrong shape"
    assert relevance_matrix.shape[1] == n, "relevance_matrix has wrong shape"

    relevances = relevance_matrix[nodes.loc[target_node.id].row, :].flatten()

    nodes.insert(1, "relevance", relevances)

    nodes.relevance[nodes.document_id == target_node.document_id] = 0

    ranked_nodes = nodes.sort_values(by="relevance", ascending=False, inplace=False)

    if threshold:
        ranked_nodes = ranked_nodes[ranked_nodes.relevance > float(threshold)]

    if count:
        ranked_nodes = ranked_nodes[:count]

    return ranked_nodes.relevance, [queryset.get(id=i) for i in ranked_nodes.index]
