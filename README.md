# alignment-prototype
Code base for a prototype for the hackathon on curriculum structure alignments.



Operations
----------
These steps should work for any of the users with sudo rights on the server,
including  `aron`, `ivan`, `jamie`, `kevin`, `kevino`, and `richard`.


### Deploy

    ssh 35.235.65.36
        sudo su
            cd /projects/alignment-prototype/
            git pull
            systemctl restart gunicorn


### Export data

    ssh 35.235.65.36
        sudo su kevino
            cd /projects/alignment-prototype/
            pipenv run alignmentpro/manage.py exportdata








TODOs
-----
 - How do we make robust/forgiving/helpful errors when bad Excel formatting?




Install
-------

    pipenv --python python3.6 install --dev



Services
--------
Assuming you have Postgres DB running on localhost, you'll need to create the
DB called `alignmentpro` using the following command:

    # make sure postgres is running
    createdb alignmentpro
    createdb standards


Setup
-----

### Frontend 

    yarn install
    yarn run build

### Backend

    ./alignmentpro/manage.py makemigrations alignmentapp  # in case some not commited
    ./alignmentpro/manage.py migrate

### Load data fixutres

    ./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/paremeters.json
    ./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/subject_areas.json
    ./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/admin_user.json

    ./alignmentpro/manage.py loaddata imports/curriculumdocuments/CCSSM.json
    ./alignmentpro/manage.py loaddata imports/curriculumdocuments/NGSS.json
    ./alignmentpro/manage.py loaddata imports/curriculumdocuments/Australia.json
    ./alignmentpro/manage.py loaddata imports/curriculumdocuments/khan_academy_us.json
    ./alignmentpro/manage.py loaddata imports/curriculumdocuments/CA-CTE.json

    ./alignmentpro/manage.py runserver



Load sample data
----------------
We've prepared some sample curriculum structures in this gsheet.

    ./alignmentpro/manage.py importchunk \
        --source_id='sample1-uganda-biology' \
        --title='Uganda biology sample topic' \
        --country='Uganda' \
        --digitization_method='scan_manual' \
        --gsheet_id='1-ei7BBMOx0udbXxyLJjMPYLW0EJWg9wFUyV9ODa8m5o' \
        --gid='1733263132'

    ./alignmentpro/manage.py importchunk \
        --source_id='sample2-kenya-math' \
        --title='Kenya sample math topics' \
        --country='Kenya' \
        --digitization_method='scan_manual' \
        --gsheet_id='1-ei7BBMOx0udbXxyLJjMPYLW0EJWg9wFUyV9ODa8m5o' \
        --gid='1031912854'

    ./alignmentpro/manage.py importchunk \
        --source_id='sample4-uganda-chemistry' \
        --title='Uganda chemistry sample topic' \
        --country='Uganda' \
        --digitization_method='scan_manual' \
        --gsheet_id='1-ei7BBMOx0udbXxyLJjMPYLW0EJWg9wFUyV9ODa8m5o' \
        --gid='1069644580'



Interactive debug
-----------------

    ./alignmentpro/manage.py shell



Data export
-----------
Use the command

    ./alignmentpro/manage.py exportdata

The option `--drafts` will also export draft curriculum docs, while specifying
`--includetestdata` will include the judgments test data.


Printing trees
--------------
Export tree by source_id

    ./alignmentpro/manage.py printtree --source_id=<source_id>

Use this command to export all Australia curriculum documents:

    ./alignmentpro/manage.py printtree  --short_identifiers --country=Australia



Importing chunkedscans folder hierarchy
---------------------------------------
Assuming the folder `files/chunkedscans/KICDvolumeII_KICD secondary curriculum volume II`
contains the sample topic chunks, use the following command to import them into DB:

    ./alignmentpro/manage.py importsectionzips --sourcedir='files/chunkedscans/KICDvolumeII_KICD secondary curriculum volume II'

This will create a document with source id `KICDvolumeII` and title `KICD secondary curriculum volume II`,
add a root `DocumentSection` with the same name as the document `KICD secondary curriculum volume II`,
then recursively create `DocumentSection` for each of the subfolders.
NOTE: this script only works for the filenames of the KICD curriculum.



Sample documents, nodes, and human judgment edge
------------------------------------------------


```python
from alignmentapp.models import CurriculumDocument, StandardNode
from alignmentapp.models import HumanRelevanceJudgment

d1, _ = CurriculumDocument.objects.get_or_create(title='KICD Math', source_id='kicd-math-sample')
n1 = StandardNode.add_root(title='KICD standards root', document=d1)
n2 = n1.add_child(title='Math', document=n1.document)
n3 = n2.add_child(title='Algebra', document=n2.document)
n4 = n2.add_child(title='Geometry', document=n2.document)

d2, _ = CurriculumDocument.objects.get_or_create(title='Uganda Math', source_id='uganda-math-sample')
n5 = StandardNode.add_root(title='NCDC Math standard root', document=d2)

e = HumanRelevanceJudgment(node1=n1, node2=n2, rating=0.7)
e.save()


print( n1.judgments.all() )   # judgments searches both node1 and node2 positions of n1
# <QuerySet [<HumanRelevanceJudgment: <StandardNode:  KICD Math standard root> <--0.7--> <StandardNode:  Uganda root node>>]>

print( n2.judgments.all() )
# <QuerySet [<HumanRelevanceJudgment: <StandardNode:  KICD Math standard root> <--0.7--> <StandardNode:  Uganda root node>>]>

```


Clean start
-----------

Delete all data and start form clean slate:

    dropdb alignmentpro
    rm -rf alignmentpro/alignmentapp/migrations/00*py
    createdb alignmentpro
    sleep 1
    ./alignmentpro/manage.py makemigrations alignmentapp
    ./alignmentpro/manage.py migrate
