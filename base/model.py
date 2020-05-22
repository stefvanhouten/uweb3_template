import binascii
import hashlib
import base64
import os

from uweb3 import model


class User(model.Record):
  """Abstraction class for the user table."""
  SALT_BYTES = 8

  @classmethod
  def FromUsername(cls, connection, username):
    """Returns a User object based on the given username."""
    with connection as cursor:
      safe_name = connection.EscapeValues(username)
      user = cursor.Select(
          table=cls.TableName(),
          conditions='username=%s' % safe_name)
    if not user:
      raise cls.NotExistError('No user with username %r' % username)
    return cls(connection, user[0])

  @classmethod
  def HashPassword(cls, password, salt=None):
    if not salt:
      salt = cls.SaltBytes()
    if (len(salt) * 3) / 4 - salt.decode('utf-8').count('=', -2) != cls.SALT_BYTES:
      raise ValueError('Salt is of incorrect length. Expected %d, got: %d' % (
          cls.SALT_BYTES, len(salt)))
    m = hashlib.sha256()
    m.update(password.encode("utf-8") + binascii.hexlify(salt))
    password = m.hexdigest()
    return { 'password': password, 'salt': salt }

  @classmethod
  def SaltBytes(cls):
    """Returns the configured number of random bytes for the salt."""
    random_bytes = os.urandom(cls.SALT_BYTES)
    return base64.b64encode(random_bytes).decode('utf-8').encode('utf-8') #we do this to cast this byte to utf-8

  def UpdatePassword(self, plaintext):
    """Stores a new password hash and salt, from the given plaintext."""
    self.update(self.HashPassword(plaintext))
    self.Save()

  def VerifyPlaintext(self, password):
    """Verifies a given plaintext password."""
    salted = self.HashPassword(password, self['salt'].encode('utf-8'))['password']
    return salted == self['password']

  @classmethod
  def FromID(cls, connection, id):
    """Get user by id."""
    with connection as cursor:
      userquery = cursor.Execute("""
                            SELECT *
                            FROM user
                            WHERE ID=%s"""
                                 % connection.EscapeValues(id))
    if userquery:
      return cls(connection, userquery[0])
    else:
      return False

  def Delete(self, connection):
    super(User, self).Delete()
