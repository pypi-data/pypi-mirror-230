import subprocess
import os

def run_django_server(path, app_name="app"):
    # Change directory to the provided path
    os.chdir(path)
    
    # Run makemigrations for the given app
    makemigrations_command = ["python", "manage.py", "makemigrations", app_name]
    subprocess.run(makemigrations_command)

    # Run migrate
    migrate_command = ["python", "manage.py", "migrate"]
    subprocess.run(migrate_command)

    # Run the Django development server
    runserver_command = ["python", "manage.py", "runserver"]
    subprocess.run(runserver_command)
