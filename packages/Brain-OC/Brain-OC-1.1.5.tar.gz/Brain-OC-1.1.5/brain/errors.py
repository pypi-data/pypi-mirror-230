# coding=utf8
""" Errors

Brain error codes
"""

__author__ = "Chris Nasr"
__copyright__ = "Ouroboros Coding Inc"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2023-01-16"

__all__ = ['body', 'SIGNIN_FAILED', 'PASSWORD_STRENGTH', 'BAD_PORTAL']

# Ouroboros imports
from body import errors as body

SIGNIN_FAILED = 1200
"""Sign In Failed"""

PASSWORD_STRENGTH = 1201
"""Password not strong enough"""

BAD_PORTAL = 1202
"""Portal doesn't exist, or the user doesn't have permissions for it"""