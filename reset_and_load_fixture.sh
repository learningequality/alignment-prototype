./alignmentpro/manage.py reset_db
#
echo "migrating..."
./alignmentpro/manage.py migrate
#
echo "Loading application constants..."
./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/paremeters.json
./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/subject_areas.json
./alignmentpro/manage.py loaddata alignmentpro/alignmentapp/fixtures/admin_user.json

#
echo "Loading data fixtures..."
./alignmentpro/manage.py loaddata imports/curriculumdocuments/CCSSM.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/NGSS.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/Australia.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/khan_academy_us.json
./alignmentpro/manage.py loaddata imports/curriculumdocuments/CA-CTE.json