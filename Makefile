build:
	yarn run build
	cd alignmentpro && python manage.py collectstatic --noinput

restart:
	sudo systemctl restart gunicorn

pull:
	git pull
	cd alignmentpro && python manage.py migrate --noinput

gunicornserver:
	cd alignmentpro && gunicorn -b 0.0.0.0:8080 --workers=9 --threads=2 alignmentpro.wsgi

update: pull build restart