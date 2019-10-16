from datetime import datetime 
import os
import numpy as np

from django.conf import settings

from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment



def prob_weighted_random(queryset, model_name='baseline', gamma=1.0):
    """
    Chooses a random row (uniform random) from all the possible ones,
    then chooses a weighted random column based on the probability and the
    relevance-favoritizm facgor `gamma`.
    """
    modeldirpath = os.path.join(settings.MODELS_BASE_DIR, model_name)
    # load the index
    node_id_lookup = np.load(os.path.join(modeldirpath, 'index.npy'))
    # load the matrix
    relevance_matrix = np.load(os.path.join(modeldirpath, 'relevance.npy'))

    n = len(node_id_lookup)
    # sanity checks
    assert relevance_matrix.shape[0] == n, 'relevance_matrix has wrong shape'
    assert relevance_matrix.shape[1] == n, 'relevance_matrix has wrong shape'

    # choose a random row
    ir = np.random.choice(n)        # choose a ranrom row index
    rowi = relevance_matrix[ir,:]   # select 
    rowi[rowi>0] = 0                # set all negative valuses zero
    rowi[ir]=0                      # set self to zero
    rowi_asp = rowi**gamma/sum(rowi**gamma)

    jr = np.random.choice(n, p=rowi_asp)

    leftid = node_id_lookup[ir]
    rightid = node_id_lookup[jr]

    return queryset.filter(id__in=[leftid,rightid])