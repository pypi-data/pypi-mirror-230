# Build

```shell
pip install -r requirements.txt
rm -fr dist
python -m build 
python -m twine upload dist/* -u __token__ -p $(PYPI_TOKEN)
```

## configuration

```yaml
device-name: server992
kafka-config:
  type: 1  # 1 is for default sasl_ssl
  value:
    bootstrap_servers:
      - { host }
    sasl_mechanism: SCRAM-SHA-256
    security_protocol: SASL_SSL
    sasl_plain_username: { username }
    sasl_plain_password: { password }
```

# Docker

1. Download the Dockerfile for build
    ```shell
    mkdir sipc
    pushd sipc
    curl https://gist.githubusercontent.com/xh-dev/3359450fd15f843016cc6f0babd8bfc0/raw/Dockerfile -O
    ```
2. Create `config.yaml` base on template in `Configuration` section.
3. build the docker image
```shell
docker build -t sipc:latest .
```
