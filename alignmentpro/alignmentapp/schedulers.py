from datetime import datetime
import os
import numpy as np
import pandas as pd

from django.conf import settings

from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


def prob_weighted_random(queryset, model_name="baseline", gamma=1.0):
    """
    Chooses a random row (uniform random) from all the possible ones,
    then chooses a weighted random column based on the probability and the
    relevance-favoritizm facgor `gamma`.
    """
    modeldirpath = os.path.join(settings.MODELS_BASE_DIR, model_name)
    # load the index
    node_id_lookup = np.load(os.path.join(modeldirpath, "index.npy"))
    # load the matrix
    relevance_matrix = np.load(os.path.join(modeldirpath, "relevance.npy"))
    # load the pickled DataFrame of nodes
    nodes = pd.read_pickle(os.path.join(modeldirpath, "nodes.pk"))

    n = len(node_id_lookup)
    # sanity checks
    assert relevance_matrix.shape[0] == n, "relevance_matrix has wrong shape"
    assert relevance_matrix.shape[1] == n, "relevance_matrix has wrong shape"

    # choose a random row
    ir = np.random.choice(n)  # choose a ranrom row index
    rowi = relevance_matrix[ir, :].flatten()  # select
    rowi[rowi < 0] = 0  # set all negative valuses zero
    rowi[
        nodes.document_id == nodes.document_id[j]
    ] = 0  # set all from same document to 0
    rowi[rowi > 0.99] = 0  # set duplicates to zero
    rowi[ir] = 0  # set self to zero
    rowi_asp = rowi ** gamma / sum(rowi ** gamma)

    jr = np.random.choice(n, p=rowi_asp)

    leftid = node_id_lookup[ir]
    rightid = node_id_lookup[jr]

    return relevance_matrix[leftid, rightid], queryset.filter(id__in=[leftid, rightid])
