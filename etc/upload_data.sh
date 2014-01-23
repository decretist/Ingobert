#!/bin/sh
bulkloader.py --url=http://localhost:8080/_ah/remote_api --kind=Capitulary --filename=upload.xml --config_file=bulkloader.yaml
# appcfg.py upload_data --config_file=bulkloader.yaml --kind=Capitulary --url=http://localhost:8080/_ah/remote_api --filename=upload.xml
# appcfg.py upload_data --config_file=bulkloader.yaml --kind=Capitulary --url=http://localhost:8080/_ah/remote_api --filename=upload.xml --email=decretist@gmail.com
# appcfg.py upload_data --config_file=bulkloader.yaml --application=dev~ingobert-app-hrd --kind=Capitulary --url=http://localhost:8080/_ah/remote_api --filename=upload.xml --email=admin
# appcfg.py upload_data --config_file=bulkloader.yaml --application=ingobert-app-hrd --kind=Capitulary --url=http://ingobert-app.appspot.com/_ah/remote_api --filename=upload.xml --email=decretist@gmail.com
