from setuptools import setup, find_packages

setup(
	name = "sog-devops-client",
	version = '1.0.2',
  author ="v-yangchao",
  author_email = "v-yangchao@sinooceangroup.com",
  long_description_content_type="text/markdown",
	long_description = open('README.md',encoding="utf-8").read(),
  python_requires=">=3.6",
  install_requires=['requests>=2.26.0', 'tenacity>=8.2.1'],
	packages = find_packages(),
 	license = 'Apache',
  classifiers = [
       'License :: OSI Approved :: Apache Software License',
       'Natural Language :: English',
       'Operating System :: OS Independent',
       'Programming Language :: Python',       
       'Programming Language :: Python :: 3.10',
       'Topic :: Software Development :: Libraries :: Python Modules',
    ],
  package_data={'': ['*.csv', '*.txt','.toml','.py']}, 
  include_package_data=True 

)
