[![IMG-20230823-151908.jpg](https://i.postimg.cc/Vsd2Qym0/IMG-20230823-151908.jpg)](https://postimg.cc/dDc5rx7J)

# Emonic Web Framework

Emonic is a lightweight web framework for building web applications in Python. It provides essential features to help you quickly develop and deploy web applications with ease.

## Features

- Routing: Define URL rules and map them to corresponding view functions.
- Templating: Use Jinja2 templates to generate dynamic HTML content.
- Static File Serving: Easily serve static files such as stylesheets, images, and scripts.
- Middleware Support: Extend functionality with custom middleware components.
- Session Management: Built-in session management for user-specific data.
- Error Handling: Define custom error handlers for different HTTP error codes.
- Blueprint System: Organize your application into modular blueprints.
- CSRF Protection: Built-in CSRF token generation and validation.

## Installation

Install and update using pip:
```shell
$ pip install emonic
```
## A Smiple Example

```python
# save this as views.py
from emonic.core import Emonic

app = Emonic(__name__)

@app.route('/')
def home(request):
    return 'Welcome to Emonic!'

if __name__ == "__main__":
    app.run() 
```
## Terminal

```python
$ python views.py
  * Running on http://127.0.0.1:8000/ (Press CTRL+C to quit)
```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests on the GitHub repository, see the [contributing guidelines](https://github.com/embrake/emonic).

## Links

- Documentation: http://emonic.vvfin.in/
- Changes: http://emonic.vvfin.in/changes/
- PyPI Releases: https://pypi.org/project/Emonic/
- Source Code: https://github.com/embrake/emonic
- Issue Tracker: https://github.com/embrake/emonic/issues 