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
    """Simple method that adds a new user to the user table."""
    username = self.post.getfirst('username')
    password = self.post.getfirst('password')
    if not username:
      #Flashing is similar to flask. Messages can be accessed under the [messages] variable in the template
      self.Flash("Username required")
      return False #Boolean that indicates if the creation of a user was success or not
    if not password:
      self.Flash("Password required")
      return False
    try:
      #This is our custom User model(found in model.py), it extends the uweb3.model.Record with custom functions
      #such as FromUsername specific for this class. self.connection is found when using PageMaker and DebuggingPagemaker.
      user = model.User.FromUsername(self.connection, username)
    except uweb3.model.NotExistError:
      hashed = model.User.HashPassword(self.post.getfirst('password'))
      user = model.User.Create(self.connection, {
          'username': username,
          'password': hashed['password'],
          'salt': hashed['salt'].decode('utf-8')})
      return True #This time we actually made the user so we return True
    else:
      self.Flash("Username is already taken")
      return False

  def ValidateLogin(self):
    try:
      #Try and validate the user based on the POST request we received.
      user = self.USER.FromUsername(
          self.connection, self.post.getfirst('username'))
      #self.post.getfirst('password', '') means we either want to get the password field if available or we default to ''
      if user.VerifyPlaintext(str(self.post.getfirst('password', ''))):
        return self._Login_Success(user)
      return self._Login_Failure()Boolean that indicates if the creation of a user was success or not
    except uweb3.model.NotExistError:
      return self._Login_Failure()

  def _Login_Success(self, user):
    """Renders the response to the user upon authentication success."""
    #We don't want our password or salt leaked out so we remove these and create a new object called secure_user.
    #This object now holds the userID and username, you could also choose to just return the userID instead.
    secure_user = { key : value for key, value in user.items() if key not in ('password', 'salt')}
    #We inherit uweb3.model.SecureCookie, which gives us access to the SecureCookie.Create method,
    #this method is used, as you might have guessed already, to create a new SecureCookie with our secure_user object.
    self.Create('login',
                secure_user,
                max_age='172800')
    #We created our cookie, and in this example we don't want to do anything else.
    #Now it is time to redirect to our loggedin users only page!
    return self.req.Redirect('/home')

  def _Login_Failure(self):
    """Renders the response to the user upon authentication failure."""
    #It seems like we have raised an uweb3.model.NotExistError, meaning no user with supplied username is found.
    #Since we don't want to tell this to the user we just return an incorrect combination error.
    self.Flash("Username/password combination is incorrect")
    #This should only be done when the index.html doesn't take any special keywords,
    #since our index.html file is quite boring we can just render it like this.
    #Generally it is better to redirect to the page so that we use the route handler instead of rendering it ourselves.
    return self.parser.Parse('index.html')


class PageMaker(uweb3.PageMaker, LoginMixin):
  """Holds all the request handlers for the application"""
  def __init__(self, *args, **kwds):
    """Overwrites the default init to add extra templateparser functions."""
    super(PageMaker, self).__init__(*args, **kwds)
    LoginMixin.__init__(self)

  def _GetUserLoggedIn(self):
    """Gets the user that is logged in from the current session."""
    #The cookiejar is an attribute inherited from the uweb3.model.SecureCookie class and stores all
    #of the created SecureCookies from our application. Since we named our SecureCookie login
    #we want to check if it is in the cookiejar or not. If it is, great! we can now login.
    #If the cookie is missing however, either the user tampered with it or it ran out.
    #in that case we don't want to allow the user to proceed with the login so we raise an Error.
    self.user = self.cookiejar.get('login')
    if self.user:
      return self.user
    #Raise our NoSessionError from the LoginMixin, since we use a try/except in our routes at this moment
    #it should be caught and we should be redirected to the index page instead.
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
    #Use the SecureCookie method Delete te remove the cookie from the cookiejar and the browser.
    #The user will not be able to access pages meant for loggedin users only!
    self.Delete("login")
    return self.req.Redirect('/home')

