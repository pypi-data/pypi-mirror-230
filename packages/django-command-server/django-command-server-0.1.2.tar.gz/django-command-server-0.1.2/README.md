# django-command-server

Django management.command is running a long live task, we make it a linux daemon server, so that you can start, stop, restart the task.

## Install

```
pip install django-command-server
```


## Usage

**app/management/commands/helloserver.py**

```
import djclick as click
from django_command_server import DjangoCommandServer

class HelloServer(DjangoCommandServer):
    def main(self):
        while True:
            print("hello")

@click.group()
def main():
    pass

hello_server = HelloServer()
hello_server.setup(main)
```

**Notes:**

- django_command_server is not a django application, do do NOT include it in django's INSTALLED_APPS.
- DjangoCommandServer setup takes a djclick.group(), so create an instance and pass it to setup.
- Implement your own server main.


## Release

### v0.1.0 2020/11/09

- First release.

### v0.1.1 2020/11/09

- Add deps in requirements.txt.

### v0.1.2 2023/09/18

- Doc update.
