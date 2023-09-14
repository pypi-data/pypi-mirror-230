# coding=utf8
""" Brain REST

Handles starting the REST server using the Brain service
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-08-25"

# Ouroboros imports
from body import errors
from config import config

# Python imports
from os import environ

# Pip imports
from RestOC import EMail, REST, Services, Session

# Module imports
from brain.service import Brain

def run():
	"""Run

	Starts the http REST server
	"""

	# Init the email module
	EMail.init(config.email({
		'error_to': 'errors@localhost',
		'from': 'admin@localhost',
		'smtp': {
			'host': 'localhost',
			'port': 587,
			'tls': True,
			'user': 'noone',
			'passwd': 'nopasswd'
		}
	}))

	# Get redis session config
	dRedis = config.redis.session({
		'host': 'localhost',
		'port': 6379,
		'db': 0,
		'charset': 'utf8'
	})

	# Init the Session module
	Session.init(dRedis)

	# Get the REST config
	dRest = config.rest({
		'allowed': 'localhost',
		'default': {
			'domain': 'localhost',
			'host': '0.0.0.0',
			'port': 8800,
			'protocol': 'http',
			'workers': 1
		},
		'services': {
			'brain': {'port': 0},
			'mouth': {'port': 1}
		}
	})

	# Create the REST config instance
	oRestConf = REST.Config(dRest)

	# Set verbose mode if requested
	if 'VERBOSE' in environ and environ['VERBOSE'] == '1':
		Services.verbose()

	# Get all the services
	dServices = {k:None for k in dRest['services']}

	# Add this service
	dServices['brain'] = Brain()

	# Register all services
	Services.register(
		dServices,
		oRestConf,
		config.services.salt(),
		config.services.internal_key_timeout(10)
	)

	# Create the HTTP server and map requests to service
	REST.Server({

		'/permissions': {'methods': REST.READ | REST.UPDATE},
		'/permissions/add': {'methods': REST.CREATE},

		'/search': {'methods': REST.READ},

		'/session': {'methods': REST.READ},

		'/signin': {'methods': REST.POST},
		'/signin/to': {'methods': REST.POST},
		'/signout': {'methods': REST.POST},

		'/user': {'methods': REST.CREATE | REST.READ | REST.UPDATE},
		'/user/email': {'methods': REST.UPDATE},
		'/user/email/verify': {'methods': REST.UPDATE},
		'/user/names': {'methods': REST.READ},
		'/user/passwd': {'methods': REST.UPDATE},
		'/user/passwd/forgot': {'methods': REST.CREATE | REST.UPDATE},
		'/user/setup': {'methods': REST.READ | REST.UPDATE},
		'/users/by/email': {'methods': REST.READ},
		'/users/by/id': {'method': REST.READ},

		'/verify': {'methods': REST.READ},

		},
		'brain',
		'https?://(.*\\.)?%s' % config.rest.allowed('localhost').replace('.', '\\.'),
		error_callback=errors.service_error
	).run(
		host=oRestConf['brain']['host'],
		port=oRestConf['brain']['port'],
		workers=oRestConf['brain']['workers'],
		timeout='timeout' in oRestConf['brain'] and oRestConf['brain']['timeout'] or 30
	)