echo "yes" | ./alignmentpro/manage.py reset_db
./alignmentpro/manage.py migrate
./alignmentpro/manage.py loaddata alignmentapp_fixtures.json 