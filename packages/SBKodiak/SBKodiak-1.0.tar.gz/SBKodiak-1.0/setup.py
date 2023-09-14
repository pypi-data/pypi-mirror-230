from distutils.core import setup

setup(name='SBKodiak',
      version='1.0',
      description='SanBlaze Python control of Kodiak Modules',
      author='Matt Holsey',
      author_email='mholsey@sanblaze.com',
      url='https://www.sanblaze.com/',
	  package_dir = {'': 'SBKodiak'},
      packages=['', 
				'Docs',
				'Tests'],
	  install_requires=[
			    'paramiko',
			    'requests',
				'urllib3',
				'sqlite3',
		  ],
     )