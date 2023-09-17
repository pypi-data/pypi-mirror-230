# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snmpsim',
 'snmpsim.commands',
 'snmpsim.grammar',
 'snmpsim.record',
 'snmpsim.record.search',
 'snmpsim.reporting',
 'snmpsim.reporting.formats',
 'snmpsim.variation']

package_data = \
{'': ['*'],
 'snmpsim': ['data/*',
             'data/1.3.6.1.6.1.1.0/*',
             'data/foreignformats/*',
             'data/mib2dev/*',
             'data/public/*',
             'data/public/1.3.6.1.2.1.100.1.2.0/*',
             'data/public/1.3.6.1.6.1.1.0/*',
             'data/recorded/*',
             'data/variation/*',
             'data/variation/multiplex/*']}

install_requires = \
['pysnmp-lextudio>=4.4.3']

entry_points = \
{'console_scripts': ['snmpsim-command-responder = '
                     'snmpsim.commands.responder:main',
                     'snmpsim-command-responder-lite = '
                     'snmpsim.commands.responder_lite:main',
                     'snmpsim-manage-records = snmpsim.commands.rec2rec:main',
                     'snmpsim-record-commands = snmpsim.commands.cmd2rec:main',
                     'snmpsim-record-mibs = snmpsim.commands.mib2rec:main',
                     'snmpsim-record-traffic = snmpsim.commands.pcap2rec:main']}

setup_kwargs = {
    'name': 'snmpsim-lextudio',
    'version': '1.0.4',
    'description': "SNMP Simulator is a tool that acts as multitude of SNMP Agents built into real physical devices, from SNMP Manager's point of view. Simulator builds and uses a database of physical devices' SNMP footprints to respond like their original counterparts do.",
    'long_description': "\nSNMP Simulator\n--------------\n[![PyPI](https://img.shields.io/pypi/v/snmpsim-lextudio.svg?maxAge=2592000)](https://pypi.org/project/snmpsim-lextudio/)\n[![PyPI Downloads](https://img.shields.io/pypi/dd/snmpsim-lextudio)](https://pypi.python.org/pypi/snmpsim-lextudio/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/snmpsim-lextudio.svg)](https://pypi.org/project/snmpsim-lextudio/)\n[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/lextudio/snmpsim/master/LICENSE.txt)\n\nThis is a pure-Python, open source and free implementation of SNMP agents simulator\ndistributed under 2-clause [BSD license](https://www.pysnmp.com/snmpsim/license.html).\n\nFeatures\n--------\n\n* SNMPv1/v2c/v3 support\n* SNMPv3 USM supports MD5/SHA/SHA224/SHA256/SHA384/SHA512 auth and\n  DES/3DES/AES128/AES192/AES256 privacy crypto algorithms\n* Runs over IPv4 and/or IPv6 transports\n* Simulates many EngineID's, each with its own set of simulated objects\n* Varies response based on SNMP Community, Context, source/destination addresses and ports\n* Can gather and store snapshots of SNMP Agents for later simulation\n* Can run simulation based on MIB files, snmpwalk and sapwalk output\n* Can gather simulation data from network traffic or tcpdump snoops\n* Can gather simulation data from external program invocation or a SQL database\n* Can trigger SNMP TRAP/INFORMs on SET operations\n* Capable to simultaneously simulate tens of thousands of Agents\n* Offers REST API based [control plane](https://www.pysnmp.com/snmpsim-control-plane)\n* Gathers and reports extensive activity metrics\n* Pure-Python, easy to deploy and highly portable\n* Can be extended by loadable Python snippets\n\nDownload\n--------\n\nSNMP simulator software is freely available for download from\n[PyPI](https://pypi.org/project/snmpsim-lextudio/) and\n[project site](https://www.pysnmp.com/snmpsim/download.html).\n\nInstallation\n------------\n\nJust run:\n\n```bash\n$ pip install snmpsim-lextudio\n```\n\nHow to use SNMP simulator\n-------------------------\n\nOnce installed, invoke `snmpsim-command-responder` and point it to a directory\nwith simulation data:\n\n```\n$ snmpsim-command-responder --data-dir=./data --agent-udpv4-endpoint=127.0.0.1:1024\n```\n\nSimulation data is stored in simple plaint-text files having OID|TYPE|VALUE\nformat:\n\n```\n$ cat ./data/public.snmprec\n1.3.6.1.2.1.1.1.0|4|Linux 2.6.25.5-smp SMP Tue Jun 19 14:58:11 CDT 2007 i686\n1.3.6.1.2.1.1.2.0|6|1.3.6.1.4.1.8072.3.2.10\n1.3.6.1.2.1.1.3.0|67|233425120\n1.3.6.1.2.1.2.2.1.6.2|4x|00127962f940\n1.3.6.1.2.1.4.22.1.3.2.192.21.54.7|64x|c3dafe61\n...\n```\n\nSimulator maps query parameters like SNMP community names, SNMPv3 contexts or\nIP addresses into data files.\n\nYou can immediately generate simulation data file by querying existing SNMP agent:\n\n```\n$ snmpsim-record-commands --agent-udpv4-endpoint=demo.pysnmp.com \\\n    --output-file=./data/public.snmprec\nSNMP version 2c, Community name: public\nQuerying UDP/IPv4 agent at 195.218.195.228:161\nAgent response timeout: 3.00 secs, retries: 3\nSending initial GETNEXT request for 1.3.6 (stop at <end-of-mib>)....\nOIDs dumped: 182, elapsed: 11.97 sec, rate: 7.00 OIDs/sec, errors: 0\n```\n\nAlternatively, you could build simulation data from a MIB file:\n\n```\n$ snmpsim-record-mibs --output-file=./data/public.snmprec \\\n    --mib-module=IF-MIB\n# MIB module: IF-MIB, from the beginning till the end\n# Starting table IF-MIB::ifTable (1.3.6.1.2.1.2.2)\n# Synthesizing row #1 of table 1.3.6.1.2.1.2.2.1\n...\n# Finished table 1.3.6.1.2.1.2.2.1 (10 rows)\n# End of IF-MIB, 177 OID(s) dumped\n```\n\nOr even sniff on the wire, recover SNMP traffic there and build simulation\ndata from it.\n\nBesides static files, SNMP simulator can be configured to call its plugin modules\nfor simulation data. We ship plugins to interface SQL and noSQL databases, file-based\nkey-value stores and other sources of information.\n\nWe maintain publicly available SNMP simulator instance at \n[demo.pysnmp.com](https://www.pysnmp.com/snmpsim/public-snmp-simulator.html). You are\nwelcome to query it as much as you wish.\n\nBesides stand-alone deployment described above, third-party\n[SNMP Simulator control plane](https://github.com/lextudio/snmpsim-control-plane)\nproject offers REST API managed mass deployment of multiple `snmpsim-command-responder`\ninstances.\n\nDocumentation\n-------------\n\nDetailed information on SNMP simulator usage could be found at\n[snmpsim site](https://www.pysnmp.com/snmpsim/).\n\nGetting help\n------------\n\nIf something does not work as expected,\n[open an issue](https://github.com/lextudio/pysnmp/issues) at GitHub or\npost your question [on Stack Overflow](https://stackoverflow.com/questions/ask)\nor try browsing snmpsim [mailing list archives](https://sourceforge.net/p/snmpsim/mailman/snmpsim-users/).\n\nFeedback and collaboration\n--------------------------\n\nI'm interested in bug reports, fixes, suggestions and improvements. Your\npull requests are very welcome!\n\nCopyright (c) 2010-2019, [Ilya Etingof](mailto:etingof@gmail.com).\nCopyright (c) 2022, [LeXtudio Inc.](mailto:support@lextudio.com).\nAll rights reserved.\n",
    'author': 'Ilya Etingof',
    'author_email': 'etingof@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/lextudio/snmpsim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
