#!/usr/bin/python
"""Request handlers for the uWeb3 project scaffold"""

import uweb3
from . import model

class LoginMixin(uweb3.model.SecureCookie):
  """Provides the Login Framework for uWeb3."""
  USER = model.User

  class NoSessionError(Exception):
    """Custom exception for user not having a (unexpired) session cookie."""

  def AddUser(self):
    username = self.post.getfirst('username')
    password = self.post.getfirst('password')
    if not username:
      self.Flash("Username required")
      return False
    if not password:
      self.Flash("Password required")
      return False
    try:
      user = model.User.FromUsername(self.connection, username)
    except uweb3.model.NotExistError:
      hashed = model.User.HashPassword(self.post.getfirst('password'))
      user = model.User.Create(self.connection, {
          'username': username,
          'password': hashed['password'],
          'salt': hashed['salt'].decode('utf-8')})
      return True
    else:
      self.Flash("Username is already taken")
      return False

  def ValidateLogin(self):
    try:
      user = self.USER.FromUsername(
          self.connection, self.post.getfirst('username'))
      if user.VerifyPlaintext(str(self.post.getfirst('password', ''))):
        return self._Login_Success(user)
      return self._Login_Failure()
    except uweb3.model.NotExistError:
      return self._Login_Failure()

  def _Login_Success(self, user):
    """Renders the response to the user upon authentication success."""
    secure_user = { key : value for key, value in user.items() if key not in ('password', 'salt')}
    self.Create('login',
                secure_user,
                max_age='172800')
    return self.req.Redirect('/home')

  def _Login_Failure(self):
    """Renders the response to the user upon authentication failure."""
    self.Flash("Username/password combination is incorrect")
    return self.parser.Parse('index.html')


class PageMaker(uweb3.PageMaker, LoginMixin):
  """Holds all the request handlers for the application"""
  def __init__(self, *args, **kwds):
    """Overwrites the default init to add extra templateparser functions."""
    super(PageMaker, self).__init__(*args, **kwds)
    LoginMixin.__init__(self)

  def _GetUserLoggedIn(self):
    """Gets the user that is logged in from the current session."""
    self.user = self.cookiejar.get('login')
    if self.user:
      return self.user
    raise self.NoSessionError("security error for session")

  def Index(self):
    """Returns the index template"""
    return self.parser.Parse('index.html', message=None)

  def FourOhFour(self, path):
    """The request could not be fulfilled, this returns a 404."""
    self.req.response.httpcode = 404
    return self.parser.Parse('404.html', path=path)

  def Signup(self):
    if self.req.method == 'POST':
      if self.AddUser():
        return self.req.Redirect('/home')
    return self.parser.Parse('signup.html', message=None)

  def Home(self):
    try:
      self._GetUserLoggedIn()
    except (uweb3.model.NotExistError, self.NoSessionError):
      return self.req.Redirect('/')
    return self.parser.Parse('home.html')

  def Logout(self):
    self.Delete("login")
    return self.req.Redirect('/home')

