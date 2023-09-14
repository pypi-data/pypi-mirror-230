from setuptools import setup

with open('README.md', 'r') as oF:
	long_description=oF.read()

setup(
	name='Brain-OC',
	version='1.1.5',
	description='Brain contains a service to manage users and permissions',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://ouroboroscoding.com/body/brain',
	project_urls={
		'Documentation': 'https://ouroboroscoding.com/body/brain',
		'Source': 'https://github.com/ouroboroscoding/brain',
		'Tracker': 'https://github.com/ouroboroscoding/brain/issues'
	},
	keywords=['rest','microservices'],
	author='Chris Nasr - Ouroboros Coding Inc.',
	author_email='chris@ouroboroscoding.com',
	license='Custom',
	packages=['brain'],
	package_data={'brain': [
		'definitions/*.json',
		'upgrades/*'
	]},
	python_requires='>=3.10',
	install_requires=[
		'Body-OC>=1.0.1',
		'Config-OC>=1.0.1,<1.1',
		'jsonb>=1.0.0,<1.1',
		'Rest-OC>=1.2.4',
		'Strings-OC>=1.0.1,<1.1',
		'Tools-OC>=1.2.1,<1.3',
		'undefined-oc>=1.0.0,<1.1',
		'Upgrade-OC>=1.0.0,<1.1'
	],
	entry_points={
		'console_scripts': ['brain=brain.__main__:cli']
	},
	zip_safe=True
)