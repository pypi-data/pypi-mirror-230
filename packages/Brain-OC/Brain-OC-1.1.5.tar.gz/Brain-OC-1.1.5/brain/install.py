# coding=utf8
""" Install

Method to install the necessary brain tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-07-12"

# Ouroboros imports
from upgrade import set_latest

# Module imports
from . import access, records, users

def install(conf):
	"""Install

	Installs required files, tables, records, etc. for the service

	Arguments:
		conf (dict): The brain config

	Returns:
		int
	"""

	# Install tables
	records.install()

	# If we don't have an admin
	if not records.User.exists('admin@ouroboroscoding.com', index='email'):

		# Install admin
		oUser = records.User({
			'email': 'admin@ouroboroscoding.com',
			'passwd': records.User.password_hash('Admin123'),
			'locale': conf['user_default_locale'],
			'first_name': 'Admin',
			'last_name': 'Istrator'
		})
		sUserId = oUser.create(changes={'user': users.SYSTEM_USER_ID})

		# Add admin permission
		oPermissions = records.Permissions({
			'user': sUserId,
			'portal': 'admin',
			'rights': {
				'brain_user': access.CREATE | access.READ | access.UPDATE,
				'brain_permission': access.READ | access.UPDATE
			}
		})
		oPermissions.create(changes={'user': users.SYSTEM_USER_ID})

	# Store the last known upgrade version
	set_latest(conf['data'], conf['module'])

	# Return OK
	return 0