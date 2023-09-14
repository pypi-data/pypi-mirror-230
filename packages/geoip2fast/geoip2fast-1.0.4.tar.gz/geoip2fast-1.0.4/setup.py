import sys, shutil
from setuptools import setup

try:
    with open("README.md",'r') as f:
        var_longDescription = f.readlines()
    var_longDescription = "".join(var_longDescription)         
except Exception as ERR:
    print("Erro ao ler o arquivo README.md %s"%(str(ERR)))
    sys.exit(1)

try:
    shutil.copy2("./geoip2fast/geoip2fast.py", "./scripts/geoip2fast")  
    shutil.copy2("./geoip2fast/import-csv2dat/geoip2dat.py", "./scripts/geoip2dat")  
except Exception as ERR:
    print("Erro ao copiar arquivos para o diretório scripts. %s"%(str(ERR)))
    sys.exit(1)
    
setup(
    name='geoip2fast',
    version='1.0.4',
    description='GeoIP2Fast is the fastest GeoIP2 country lookup library. A search takes less than 0.00003 seconds. It has its own data file updated with Maxmind-Geolite2-CSV and is Pure Python!',
    url='https://github.com/rabuchaim/geoip2fast',
    author='Ricardo Abuchaim',
    author_email='ricardoabuchaim@gmail.com',
    maintainer='Ricardo Abuchaim',
    maintainer_email='ricardoabuchaim@gmail.com',
    bugtrack_url='https://github.com/rabuchaim/geoip2fast/issues',
    license='MIT',
    packages=['geoip2fast'],
    keywords=['geoip','geoip2','geolite2','geo ip','ip','geo','geolocation','geoip2fast','pure-python','purepython','pure python','geoiptoofast','maxmind','geoip2dat'],
    package_dir = {'geoip2fast': 'geoip2fast'},
    package_data={
        'geoip2fast': ['geoip2fast.dat.gz','geoip2fast-20230913.txt','import-csv2dat/geoip2dat.py','tests/geoip2fast_test.py','tests/speed_test.py','tests/coverage_test.py','tests/compare_with_mmdb.py','tests/random_test.py','tests/geoipcli.py'],
    },
    scripts=['scripts/geoip2dat','scripts/geoip2fast'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',  
        'Programming Language :: Python :: 3.11',          
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    include_package_data=True,
    long_description=f"""{var_longDescription}""",
    long_description_content_type='text/markdown',    
)
''