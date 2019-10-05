# alignment-prototype
Code base for a prototype for the alignment hackathon


Install
-------

    pipenv install


Services
--------

    # start postgres
    createdb alignmentpro

Setup
-----

    ./alignmentpro/manage.py makemigrations alignmentapp
    ./alignmentpro/manage.py migrate



Sample documents, nodes, and human judgment edge
------------------------------------------------


```python

from alignmentapp.models import CurriculumDocument, StandardNode, LearningObjective
from alignmentapp.models import HumanRelevanceJudgment

d1 = CurriculumDocument(title='KICD Math')
d1.save()
n1 = StandardNode.add_root(title='KICD Math standard root', document=d1)

d2 = CurriculumDocument(title='Uganda Math')
d2.save()
n2 = StandardNode.add_root(title='NCDC Math standard root', document=d2)

e = HumanRelevanceJudgment(node1=n1, node2=n2, rating=0.7)
e.save()


print( n1.judgments.all() )   # judgments searches both node1 and node2 positions of n1
# <QuerySet [<HumanRelevanceJudgment: <StandardNode:  KICD Math standard root> <--0.7--> <StandardNode:  Uganda root node>>]>

print( n2.judgments.all() )
# <QuerySet [<HumanRelevanceJudgment: <StandardNode:  KICD Math standard root> <--0.7--> <StandardNode:  Uganda root node>>]>
```



### TODOs

```python
n.top_related(num_nodes, qssearch=None, mlmodel?)
HumanRelevanceJudgment.objects.by_nodes([n1]) ?
```



Feature vectors
---------------

```python
from alignmentapp.models import CurriculumDocument, StandardNode, LearningObjective
from alignmentapp.models import StandardNodeFeatureVector

d1 = CurriculumDocument(title='KICD Math')
d1.save()
n1 = StandardNode.add_root(title='KICD Math standard root', document=d1)


vec = list(i/3123 for i in range(0,1000))
n1v1 = StandardNodeFeatureVector(node=n1, model_version=1, data=vec)
n1v1.save()

n1.features.all()
# QuerySet [<StandardNodeFeatureVector: StandardNodeFeatureVector object (1)>
```


### TODOs

  - `.raw`  SQL query to get top-vectors by cosine similarity
    http://sciencesql.blogspot.com/2016/03/calculating-cosine-similarity-between.html
    or https://www.slideshare.net/GarySieling/word2vec-in-postgres
    maybe https://github.com/guenthermi/postgres-word2vec

