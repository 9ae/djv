djv
===

Deja Vu - The VideoX Hackathon Project

Setup
-----

Following are steps to create a new development environment.

1. Create new Virtualenv in your local project and activate environment.

        cd /path/to/git/project
        virtualenv .venv
        source .venv/bin/activate

2. Install project dependencies using Pip.

        pip install -r requires.txt

3. Create local Sqlite database.

        python manage.py syncdb

4. Run development HTTP server.

        python manage.py runserver

iOS: https://github.com/IRIS089/DejaVu
