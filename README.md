# alignment-prototype
Code base for a prototype for the alignment hackathon


Install
-------

    pipenv install


Setup
-----

    ./alignmentpro/manage.py makemigrations
    ./alignmentpro/manage.py migrate



Sample code
-----------

```python
d1 = CurriculumDocument(title='KICD Math')
n1 = StandardNode.add_root(title='rootnode of KICD', document=d1)


d2 = CurriculumDocument(title='Uganda Math')
n2 = StandardNode.add_root(title='Uganda root node', document=d2)

e = AlignmentEdge(source=n1, target=n2)
e.save()

n1.relevantfor.all()
# <QuerySet [<AlignmentEdge: AlignmentEdge object (1)>]>

n2.related.all()
# <QuerySet [<AlignmentEdge: AlignmentEdge object (1)>]>
```


Caveats:
  - nothing prevents us from adding multiple root nodes (must enforce somehow)
