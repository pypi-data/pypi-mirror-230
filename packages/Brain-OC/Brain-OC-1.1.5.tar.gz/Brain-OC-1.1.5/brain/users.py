# coding=utf8
""" Users

Shared methods for accessing user info
"""

__author__ = "Chris Nasr"
__copyright__ = "Ouroboros Coding Inc"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2022-08-29"

# Ouroboros modules
import undefined

# Python imports
from typing import List

# Pip imports
from RestOC.Services import internal_key, read, ResponseException

SYSTEM_USER_ID = '00000000-0000-0000-0000-000000000000'
"""System User ID"""

RIGHTS_ALL_ID = '01234567-9abc-4def-a012-3456789abcde'
"""Used to represent rights across the entire system"""

def details(
	_id: str | List[str],
	fields: List[str] = None,
	order: List[str] = None,
	as_dict: bool | str = '_id'
) -> dict | list:
	"""Details

	Fetches user info from IDs

	Arguments:
		_id (str|str[]) The ID(s) to fetch info for
		fields (str[]): The list of fields to return
		order (str[]): The list of fields to order by
		as_dict (bool): Optional, if not set/true, returns a list, if set, must
						be a field that's passed

	Returns:
		dict | list
	"""

	# Init the data by adding the ID(s) and the internal key
	dData = {
		'_internal_': internal_key(),
		'_id': _id
	}

	# If we want specific fields
	if fields:
		dData['fields'] = fields

	# If we want a specific order
	if order:
		dData['order'] = order

	# Make the read using an internal key
	oResponse = read('brain', 'users/by/id', {
		'data': dData
	})

	# If there's an error
	if oResponse.error_exists():

		# Throw it
		raise ResponseException(oResponse)

	# If we don't want a dict
	if not as_dict:
		return oResponse.data

	# Convert the data into a dictionary
	dUsers = {}
	for d in oResponse.data:

		# Pop off the field used as a key
		sKey = d.pop(as_dict)

		# Store the rest by the key
		dUsers[sKey] = d

	# Return the users
	return dUsers

def exists(
	_id: str | List[str]
) -> bool:
	"""Exists

	Returns true if all User IDs passed exist in the system

	Arguments:
		_id (str | str[]): One or more IDs to check

	Returns:
		bool
	"""

	# Init the data by adding the ID(s) and the internal key
	dData = {
		'_internal_': internal_key(),
		'_id': _id,
		'fields': ['_id']
	}

	# Make the read using an internal key
	oResponse = read('brain', 'users/by/id', {
		'data': dData
	})

	# If there's an error
	if oResponse.error_exists():

		# Throw it
		raise ResponseException(oResponse)

	# If we got a string
	if isinstance(_id, str):

		# Set the return based on whether we got anything or not
		bRet = oResponse.data and True or False

	# Else, we got a list
	else:

		# Set the return based on if the counts match
		bRet = len(_id) == len(oResponse.data)

	# Return
	return bRet

def permissions(
	_id: str,
	portal: str = undefined
) -> dict:
	"""Permissions

	Returns the list of permissions for the user and given portal. Defaults to
	'' portal

	Arguments:
		_id (str): The ID of the user to fetch permissions for
		portal (str): Optional, the specific set of permissions to return for \
						the user

	Returns:
		dict | None
	"""

	# Make the read using an internal key
	oResponse = read('brain', 'permissions', { 'data': {
		'_internal_': internal_key(),
		'user': _id
	}})

	# If there's an error
	if oResponse.error_exists():

		# Throw it
		raise ResponseException(oResponse)

	# If we didn't get any permissions
	if not oResponse.data:
		return None

	# Organize them by portal
	dPermissions = {}
	for d in oResponse.data:
		dPermissions[d['portal']] = d['rights']

	# If we wanted all permissions
	if portal is undefined:
		return dPermissions

	# Return the portal or None
	try:
		return dPermissions[portal]
	except KeyError:
		return None