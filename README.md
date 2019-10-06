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
    ./alignmentpro/manage.py createsuperuser --username admin --email a@b.c



Interactive debug
-----------------

    ./alignmentpro/manage.py shell





Sample documents, nodes, and human judgment edge
------------------------------------------------


```python
from alignmentapp.models import CurriculumDocument, StandardNode, LearningObjective
from alignmentapp.models import HumanRelevanceJudgment

d1 = CurriculumDocument.objects.create(title='KICD Math')
n1 = StandardNode.add_root(title='KICD standards root', document=d1)
n2 = n1.add_child(title='Math', document=n1.document)
n3 = n2.add_child(title='Algebra', document=n2.document)
n4 = n2.add_child(title='Geometry', document=n2.document)

d2 = CurriculumDocument.objects.create(title='Uganda Math')
n5 = StandardNode.add_root(title='NCDC Math standard root', document=d2)

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
from alignmentapp.models import MachineLearningModel, StandardNodeFeatureVector

d1 = CurriculumDocument.objects.create(title='KICD Math')
n1 = StandardNode.add_root(title='KICD Math standard root', document=d1)
model1 = MachineLearningModel.objects.create(model_name="sentence_embeddings", model_version=1, git_hash='fefefe')

v1data = list(i/3123 for i in range(0,1000))
m1n1v1 = StandardNodeFeatureVector.objects.create(mlmodel=model1, node=n1, data=v1data)
v2data = list(i/123 for i in range(0,1000))
m1n1v1 = StandardNodeFeatureVector.objects.create(mlmodel=model1, node=n1, data=v2data)
# TODO: test with numpy array

print( n1.features.all() )
# <QuerySet [<StandardNodeFeatureVector: StandardNodeFeatureVector object (1)>, <StandardNodeFeatureVector: StandardNodeFeatureVector object (2)>]>

print( model1.feature_vectors.all() )
#  <QuerySet [<StandardNodeFeatureVector: StandardNodeFeatureVector object (1)>, <StandardNodeFeatureVector: StandardNodeFeatureVector object (2)>]>

```


### TODOs

  - `.raw`  SQL query to get top-vectors by cosine similarity
    http://sciencesql.blogspot.com/2016/03/calculating-cosine-similarity-between.html
    or https://www.slideshare.net/GarySieling/word2vec-in-postgres
    maybe https://github.com/guenthermi/postgres-word2vec





Clean start
-----------

Delete all data and start form clean slate:

    dropdb alignmentpro
    rm -rf alignmentpro/alignmentapp/migrations/00*py
    createdb alignmentpro
    sleep 1
    ./alignmentpro/manage.py makemigrations alignmentapp
    ./alignmentpro/manage.py migrate
