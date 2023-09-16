## Wake-on-LAN redirect proxy

Brutally simple, single file, Fast API based proxy service. Create a simple `path` and/or  `hostname` based
redirects that send WoL packets if target URL is not reachable. Only works for `HTTP(S)` redirects.

Great complement for a simple [auto-suspend](https://autosuspend.readthedocs.io/) setup,
e.g. your home jellyfin server or any other `HTTP` service.

That's it!

### Installation
#### From source:
```shell
poetry install
```
#### From PyPi:
```shell
pip install
```

### Run

```shell
$ ./app.py --host "0.0.0.0" --port 12345
```

### Configuration
Specify a list of proxy mappings using a yaml config, e.g.:

1. This will WoL redirect any HTTP request and carry over the path.
    e.g.: POST: http://my-proxy.home/login -> POST "http://my-jellyfin.home:8096/login"
```yaml
targets:
- handler: "wol"
  source_url: "http://my-proxy.home/*"
  target_url: "http://my-jellyfin.home:8096"
  methods: [GET, POST, DELETE, PATCH]
  options:
    mac: "75:55:39:a4:33:27"
    timeout_s: 2
```

```yaml
#  This will WoL redirect any HTTP request and carry over the path.
#  e.g.: POST: http://my-proxy.home/login -> POST "http://my-jellyfin.home:8096/login"

targets:
- handler: "wol"
  source_url: "http://my-proxy.home/*"
  target_url: "http://my-jellyfin.home:8096"
  methods: [GET, POST, DELETE, PATCH]
  options:
    mac: "75:55:39:a4:33:27"
    timeout_s: 2
```

```yaml
#  Multiple redirects to different services by hostname
#  (requires working DNS setup)

targets:
- handler: "plain"
  source_url: "http://jellyfin.home/*"
  target_url: "http://192.168.0.124:8096"
  methods: [GET, POST, DELETE, PATCH]
  
- handler: "plain"
  source_url: "http://nextcloud.home/*"
  target_url: "http://192.168.0.129:8080"
  methods: [GET, POST]
  
- handler: "plain"
  source_url: "http://torrent-box.home/*"
  target_url: "http://192.168.0.135:8080"
  methods: [GET, POST]
```

### Use as a systemd service

1. clone
```shell
git clone https://github.com/jonasbrauer/wol-redirect-proxy.git && cd wol-redirect-proxy
```

2. edit your configuration
```shell
cp example-config.yaml config.yaml
```

3. setup your virtualenv
```shell
$ python3.9 -m venv .
$ source ./bin/activate
$ (wol-redirect-proxy) pip install -r requirements.txt
```

4. create & start the systemd service
```shell
sudo cp sample-systemd.unit /etc/systemd/system/wol-redirect-proxy.service  # ...and edit user/group
sudo systemctl daemon-reload
sudo systemctl enable --now wol-redirect-proxy.service
sudo systemctl status wol-redirect-proxy.service
```
