# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['meetbot_messages']

package_data = \
{'': ['*']}

install_requires = \
['coverage[toml]>=7.0.0', 'fedora-messaging>=3.3.0,<4.0.0']

entry_points = \
{'fedora.messages': ['meetbot.meeting.complete = '
                     'meetbot_messages.meeting:MeetingCompleteV1',
                     'meetbot.meeting.start = '
                     'meetbot_messages.meeting:MeetingStartV1']}

setup_kwargs = {
    'name': 'meetbot-messages',
    'version': '1.0.1',
    'description': 'A schema package for messages sent by meetbot',
    'long_description': '# meetbot messages\n\nA schema package for [meetbot](http://github.com/fedora-infra/meetbot-messages).\n\nSee the [detailed documentation](https://fedora-messaging.readthedocs.io/en/latest/messages.html) on packaging your schemas.\n',
    'author': 'Fedora Infrastructure Team',
    'author_email': 'infrastructure@lists.fedoraproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/fedora-infra/meetbot-messages',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
