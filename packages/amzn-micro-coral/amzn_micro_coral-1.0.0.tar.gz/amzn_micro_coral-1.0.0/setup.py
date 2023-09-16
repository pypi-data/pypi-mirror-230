# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amzn_micro_coral',
 'amzn_micro_coral.auth',
 'amzn_micro_coral.clients',
 'amzn_micro_coral.util']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.2,<2.0.0', 'requests>=2.31.0,<3.0.0']

extras_require = \
{'midway': ['requests-kerberos>=0.14.0,<0.15.0'],
 'sigv4': ['requests-auth-aws-sigv4>=0.7,<0.8', 'boto3>=1.28.37,<2.0.0']}

setup_kwargs = {
    'name': 'amzn-micro-coral',
    'version': '1.0.0',
    'description': "Minimal Coral interface for when you can't use a prepackaged client.",
    'long_description': '# amzn-micro-coral\n\nA minimalistic implementation of a Coral client, used mainly for\npeople who are working in contexts where they may not be able to\nimport Coral clients directly.\n\n## Usage\n\nService calls are entirely unopinionated, so you better be good at\nreading Coral client configs. A regular instantiation of the service\nwould be:\n\n    from amzn_micro_coral import CoralService, CoralAuth\n\n    my_service = CoralService(\n        url="https://my-service.amazon.com",\n        auth=CoralAuth.midway(sentry=False),\n    )\n\n    r = my_service.post("MyService.MyOperation", data={"param1": "value1"})\n    result = r.json()\n\nThe client does do a basic level of error checking in case the Coral\nservice returns the standard error message in the form `{"__type":\n"<message>"}`.\n\n## Samples\n\nThis module also provides some very basic classes for interacting with\ngeneric services:\n\n    from amzn_micro_coral import crux\n\n    r = crux.post(<...>)\n\nSome may provide more features than others but have no guarantee of\nalways working into the future.\n',
    'author': 'Chad Crawford',
    'author_email': 'chadcr@amazon.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
