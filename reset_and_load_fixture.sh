echo "yes" | ./alignmentpro/manage.py reset_db
./alignmentpro/manage.py migrate
./alignmentpro/manage.py loaddata imports/curriculumdocuments/CCSSM.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/NGSS.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/Australia.json
