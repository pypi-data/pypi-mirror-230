# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wol_proxy']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.94.1,<0.95.0',
 'ping3>=4.0.4,<5.0.0',
 'pyyaml>=6.0,<7.0',
 'uvicorn>=0.21.0,<0.22.0',
 'wakeonlan>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['wol-proxy = wol_proxy.app:main']}

setup_kwargs = {
    'name': 'wol-redirect-proxy',
    'version': '1.0.0',
    'description': 'A simple python Wake-on-LAN proxy',
    'long_description': '## Wake-on-LAN redirect proxy\n\nBrutally simple, single file, Fast API based proxy service. Create a simple `path` and/or  `hostname` based\nredirects that send WoL packets if target URL is not reachable. Only works for `HTTP(S)` redirects.\n\nGreat complement for a simple [auto-suspend](https://autosuspend.readthedocs.io/) setup,\ne.g. your home jellyfin server or any other `HTTP` service.\n\nThat\'s it!\n\n### Installation\n#### From source:\n```shell\npoetry install\n```\n#### From PyPi:\n```shell\npip install\n```\n\n### Run\n\n```shell\n$ ./app.py --host "0.0.0.0" --port 12345\n```\n\n### Configuration\nSpecify a list of proxy mappings using a yaml config, e.g.:\n\n1. This will WoL redirect any HTTP request and carry over the path.\n    e.g.: POST: http://my-proxy.home/login -> POST "http://my-jellyfin.home:8096/login"\n```yaml\ntargets:\n- handler: "wol"\n  source_url: "http://my-proxy.home/*"\n  target_url: "http://my-jellyfin.home:8096"\n  methods: [GET, POST, DELETE, PATCH]\n  options:\n    mac: "75:55:39:a4:33:27"\n    timeout_s: 2\n```\n\n```yaml\n#  This will WoL redirect any HTTP request and carry over the path.\n#  e.g.: POST: http://my-proxy.home/login -> POST "http://my-jellyfin.home:8096/login"\n\ntargets:\n- handler: "wol"\n  source_url: "http://my-proxy.home/*"\n  target_url: "http://my-jellyfin.home:8096"\n  methods: [GET, POST, DELETE, PATCH]\n  options:\n    mac: "75:55:39:a4:33:27"\n    timeout_s: 2\n```\n\n```yaml\n#  Multiple redirects to different services by hostname\n#  (requires working DNS setup)\n\ntargets:\n- handler: "plain"\n  source_url: "http://jellyfin.home/*"\n  target_url: "http://192.168.0.124:8096"\n  methods: [GET, POST, DELETE, PATCH]\n  \n- handler: "plain"\n  source_url: "http://nextcloud.home/*"\n  target_url: "http://192.168.0.129:8080"\n  methods: [GET, POST]\n  \n- handler: "plain"\n  source_url: "http://torrent-box.home/*"\n  target_url: "http://192.168.0.135:8080"\n  methods: [GET, POST]\n```\n\n### Use as a systemd service\n\n1. clone\n```shell\ngit clone https://github.com/jonasbrauer/wol-redirect-proxy.git && cd wol-redirect-proxy\n```\n\n2. edit your configuration\n```shell\ncp example-config.yaml config.yaml\n```\n\n3. setup your virtualenv\n```shell\n$ python3.9 -m venv .\n$ source ./bin/activate\n$ (wol-redirect-proxy) pip install -r requirements.txt\n```\n\n4. create & start the systemd service\n```shell\nsudo cp sample-systemd.unit /etc/systemd/system/wol-redirect-proxy.service  # ...and edit user/group\nsudo systemctl daemon-reload\nsudo systemctl enable --now wol-redirect-proxy.service\nsudo systemctl status wol-redirect-proxy.service\n```\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
