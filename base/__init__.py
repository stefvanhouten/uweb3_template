"""A minimal uWeb3 project scaffold."""

# Standard modules
import os

# Third-party modules
import uweb3

# Application
from . import pages

def main(sio=None):
  """Creates a uWeb3 application.

  The application is created from the following components:

  - The presenter class (PageMaker) which implements the request handlers.
  - The routes iterable, where each 2-tuple defines a url-pattern and the
    name of a presenter method which should handle it.
  - The configuration file (ini format) from which settings should be read.
  """
  path = os.path.dirname(os.path.abspath(__file__))
  routes = [
      ('/', 'Index'),
      ('/signup', 'Signup'),
      ('/home', 'Home'),
      ('/login', 'ValidateLogin'),
      ('/logout', 'Logout'),
      ('/(.*)', 'FourOhFour'),
      ]
  return uweb3.uWeb(pages.PageMaker, routes, executing_path=path)
