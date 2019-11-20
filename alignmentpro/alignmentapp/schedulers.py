from datetime import datetime
import os
import numpy as np
import pandas as pd
import random

from django.conf import settings

from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


def prob_weighted_random(
    queryset,
    model_name="baseline",
    gamma=3.0,
    left_root_id=None,
    right_root_id=None,
    allow_same_doc=False,
    include_nonleaf_nodes=False,
):
    """
    Chooses a random row (uniform random) from all the possible ones,
    then chooses a weighted random column based on the probability and the
    relevance-favoritism factor `gamma`.
    """

    modeldirpath = os.path.join(settings.MODELS_BASE_DIR, model_name)

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

    queryset = queryset.filter(id__in=node_id_lookup)
    left_queryset = queryset
    right_queryset = queryset

    if not include_nonleaf_nodes:
        left_queryset = left_queryset.filter(numchild=0)
        right_queryset = right_queryset.filter(numchild=0)

    # filter down and choose a random left-hand side node
    if left_root_id is not None:
        left_ancestor_root = queryset.get(id=left_root_id)
        left_queryset = left_queryset.filter(path__startswith=left_ancestor_root.path)
    left_index = nodes.row.loc[left_queryset.values_list("id", flat=True)]

    ir = random.choice(list(left_index))  # choose a random row index for the left side
    leftid = node_id_lookup[ir]
    leftnode = queryset.get(id=leftid)

    # filter down the right-hand side queryset
    if not allow_same_doc:
        right_queryset = right_queryset.exclude(document_id=leftnode.document_id)
    if right_root_id is not None:
        right_ancestor_root = queryset.get(id=right_root_id)
        right_queryset = right_queryset.filter(
            path__startswith=right_ancestor_root.path
        )
    right_index = nodes.row.loc[right_queryset.values_list("id", flat=True)]

    # build a probability distribution for choosing the right-hand node
    rowi = relevance_matrix[ir, :].flatten()  # select row

    # exclude right-hand side columns based on the queryset
    columns_to_include = np.indices(rowi.shape)
    columns_to_exclude = np.setxor1d(columns_to_include, right_index)
    rowi[columns_to_exclude] = 0

    rowi[rowi < 0] = 0  # ignore any with negative values
    rowi[rowi > 0.999] = 0  # ignore any that are virtually identical

    # skew the distribution by gamma exponent, normalize, and select a weighted random item
    rowi_asp = rowi ** gamma / sum(rowi ** gamma)
    rowi_asp[np.isnan(rowi_asp)] = 0
    if sum(rowi_asp) == 0:
        rowi_asp = rowi
    jr = np.random.choice(n, p=rowi_asp)
    rightid = node_id_lookup[jr]
    rightnode = queryset.get(id=rightid)

    return (
        relevance_matrix[ir, jr],
        rowi_asp[jr],
        list(reversed(sorted(rowi_asp[rowi_asp > 0.001])))[:20],
        queryset.filter(id__in=[leftid, rightid]),
    )
