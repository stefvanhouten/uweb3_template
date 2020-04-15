import uweb3

class CustomRoute(uweb3.PageMaker):
  """Holds all the request handlers for the application"""

  def HelloWorld(self):
    """Returns the index template"""
    return self.parser.Parse('custom.html')
