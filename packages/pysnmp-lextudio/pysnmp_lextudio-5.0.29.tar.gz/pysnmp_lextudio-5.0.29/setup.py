# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysnmp',
 'pysnmp.carrier',
 'pysnmp.carrier.asyncio',
 'pysnmp.carrier.asyncio.dgram',
 'pysnmp.carrier.asyncore',
 'pysnmp.carrier.asyncore.dgram',
 'pysnmp.carrier.asynsock',
 'pysnmp.carrier.asynsock.dgram',
 'pysnmp.entity',
 'pysnmp.entity.rfc3413',
 'pysnmp.entity.rfc3413.oneliner',
 'pysnmp.hlapi',
 'pysnmp.hlapi.asyncio',
 'pysnmp.hlapi.asyncore',
 'pysnmp.hlapi.asyncore.sync',
 'pysnmp.hlapi.asyncore.sync.compat',
 'pysnmp.proto',
 'pysnmp.proto.acmod',
 'pysnmp.proto.api',
 'pysnmp.proto.mpmod',
 'pysnmp.proto.proxy',
 'pysnmp.proto.secmod',
 'pysnmp.proto.secmod.eso',
 'pysnmp.proto.secmod.eso.priv',
 'pysnmp.proto.secmod.rfc3414',
 'pysnmp.proto.secmod.rfc3414.auth',
 'pysnmp.proto.secmod.rfc3414.priv',
 'pysnmp.proto.secmod.rfc3826',
 'pysnmp.proto.secmod.rfc3826.priv',
 'pysnmp.proto.secmod.rfc7860',
 'pysnmp.proto.secmod.rfc7860.auth',
 'pysnmp.smi',
 'pysnmp.smi.mibs',
 'pysnmp.smi.mibs.instances']

package_data = \
{'': ['*']}

install_requires = \
['pyasn1>=0.4.8,<0.5.0',
 'pysmi-lextudio>=1.0.4,<2.0.0',
 'pysnmpcrypto>=0.0.4,<0.0.5']

setup_kwargs = {
    'name': 'pysnmp-lextudio',
    'version': '5.0.29',
    'description': '',
    'long_description': '\nSNMP Library for Python\n-----------------------\n\n[![PyPI](https://img.shields.io/pypi/v/pysnmp-lextudio.svg)](https://pypi.python.org/pypi/pysnmp-lextudio)\n[![PyPI Downloads](https://img.shields.io/pypi/dd/pysnmp-lextudio)](https://pypi.python.org/pypi/pysnmp-lextudio/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/pysnmp-lextudio.svg)](https://pypi.python.org/pypi/pysnmp-lextudio/)\n[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/lextudio/pysnmp/master/LICENSE.rst)\n\nThis is a pure-Python, open source and free implementation of v1/v2c/v3\nSNMP engine distributed under 2-clause [BSD license](https://www.pysnmp.com/pysnmp/license.html).\n\nThe PySNMP project was initially sponsored by a [PSF](http://www.python.org/psf/) grant.\nThank you!\n\nThis version is a fork of Ilya Etingof\'s project [etingof/pysnmp](https://github.com/etingof/pysnmp). Ilya sadly passed away on 10-Aug-2022. Announcement [here](https://lists.openstack.org/pipermail/openstack-discuss/2022-August/030062.html).  His work is still of great use to the Python community and he will be missed.\n\nFeatures\n--------\n\n* Complete SNMPv1/v2c and SNMPv3 support\n* SMI framework for resolving MIB information and implementing SMI\n  Managed Objects\n* Complete SNMP entity implementation\n* USM Extended Security Options support (3DES, 192/256-bit AES encryption)\n* Extensible network transports framework (UDP/IPv4, UDP/IPv6)\n* Asynchronous socket-based IO API support\n* [Asyncio](https://docs.python.org/3/library/asyncio.html) integration\n* [PySMI](https://www.pysnmp.com/pysmi/) integration for dynamic MIB compilation\n* Built-in instrumentation exposing protocol engine operations\n* Python eggs and py2exe friendly\n* 100% Python, works with Python 3.7+\n* MT-safe (if SnmpEngine is thread-local)\n\nFeatures, specific to SNMPv3 model include:\n\n* USM authentication (MD5/SHA-1/SHA-2) and privacy (DES/AES) protocols (RFC3414, RFC7860)\n* View-based access control to use with any SNMP model (RFC3415)\n* Built-in SNMP proxy PDU converter for building multi-lingual\n  SNMP entities (RFC2576)\n* Remote SNMP engine configuration\n* Optional SNMP engine discovery\n* Shipped with standard SNMP applications (RC3413)\n\n\nDownload & Install\n------------------\n\nThe PySNMP software is freely available for download from [PyPI](https://pypi.python.org/pypi/pysnmp-lextudio)\nand [GitHub](https://github.com/lextudio/pysnmp.git).\n\nJust run:\n\n```bash\n$ pip install pysnmp-lextudio\n```\n\nTo download and install PySNMP along with its dependencies:\n\n<!-- Need to find an alternate location for the links to pysnmp.com -->\n* [PyASN1](https://pyasn1.readthedocs.io)\n* [PySMI](https://www.pysnmp.com/pysmi/) (required for MIB services only)\n* Optional [pysnmpcrypto](https://github.com/etingof/pysnmpcrypto) package\n  whenever strong SNMPv3 encryption is desired\n\nBesides the library, command-line [SNMP utilities](https://github.com/lextudio/snmpclitools)\nwritten in pure-Python could be installed via:\n\n```bash\n$ pip install snmpclitools-lextudio\n```\n\nand used in the very similar manner as conventional Net-SNMP tools:\n\n```bash\n$ snmpget.py -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 demo.pysnmp.com sysDescr.0\nSNMPv2-MIB::sysDescr.0 = STRING: Linux zeus 4.8.6.5-smp #2 SMP Sun Nov 13 14:58:11 CDT 2016 i686\n```\n\nExamples\n--------\n\nPySNMP is designed in a layered fashion. Top-level and easiest to use API is known as\n*hlapi*. Here\'s a quick example on how to SNMP GET:\n\n```python\nimport asyncio\nfrom pysnmp.hlapi.asyncio.slim import Slim\nfrom pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType\n\nasync def run():\n    slim = Slim(1)\n    errorIndication, errorStatus, errorIndex, varBinds = await slim.get(\n        \'public\',\n        \'demo.pysnmp.com\',\n        161,\n        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),\n    )\n\n    if errorIndication:\n        print(errorIndication)\n    elif errorStatus:\n        print(\n            "{} at {}".format(\n                errorStatus.prettyPrint(),\n                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",\n            )\n        )\n    else:\n        for varBind in varBinds:\n            print(" = ".join([x.prettyPrint() for x in varBind]))\n\n    slim.close()\n\n\nasyncio.run(run())\n```\n\nThis is how to send SNMP TRAP:\n\n```python\nimport asyncio\nfrom pysnmp.hlapi.asyncio import *\n\nasync def run():\n    snmpEngine = SnmpEngine()\n    errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(\n        snmpEngine,\n        CommunityData(\'public\', mpModel=0),\n        UdpTransportTarget((\'demo.pysnmp.com\', 162)),\n        ContextData(),\n        "trap",\n        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(\n            ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),\n            ("1.3.6.1.2.1.1.1.0", OctetString("my system")),\n        ),\n    )\n\n    if errorIndication:\n        print(errorIndication)\n\n    snmpEngine.transportDispatcher.closeDispatcher()\n\nasyncio.run(run())\n```\n\n> We maintain publicly available SNMP Agent and TRAP sink at\n> [demo.pysnmp.com](https://www.pysnmp.com/snmpsim/public-snmp-agent-simulator.html). You are\n> welcome to use it while experimenting with whatever SNMP software you deal with.\n\n```bash\n$ python3 examples/hlapi/asyncio/manager/cmdgen/usm-sha-aes128.py\nSNMPv2-MIB::sysDescr.0 = SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m\n$\n$ python3 examples//hlapi/asyncore/sync/agent/ntforg/v3-inform.py\nSNMPv2-MIB::sysUpTime.0 = 0\nSNMPv2-MIB::snmpTrapOID.0 = SNMPv2-MIB::warmStart\nSNMPv2-MIB::sysName.0 = system name\n```\n\nOther than that, PySNMP is capable to automatically fetch and use required MIBs from HTTP, FTP sites\nor local directories. You could configure any MIB source available to you (including\n[this one](https://github.com/lextudio/mibs.snmplabs.com/tree/master/asn1)) for that purpose.\n\nFor more example scripts please refer to [examples section](https://www.pysnmp.com/pysnmp/examples/index.html#high-level-snmp)\nat pysnmp web site.\n\nDocumentation\n-------------\n\nLibrary documentation and examples can be found at the [pysnmp project site](https://www.pysnmp.com/pysnmp/).\n\nIf something does not work as expected, please\n[open an issue](https://github.com/lextudio/pysnmp/issues) at GitHub or\npost your question [on Stack Overflow](http://stackoverflow.com/questions/ask) or try browsing pysnmp\n[mailing list archives](https://sourceforge.net/p/pysnmp/mailman/pysnmp-users/).\n\nBug reports and PRs are appreciated! ;-)\n\nCopyright (c) 2005-2019, [Ilya Etingof](https://lists.openstack.org/pipermail/openstack-discuss/2022-August/030062.html).\nCopyright (c) 2022-2023, [LeXtudio Inc](mailto:support@lextudio.com).\nAll rights reserved.\n',
    'author': 'Ilya Etingof',
    'author_email': 'etingof@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/lextudio/pysnmp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
