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
      - {host}
    sasl_mechanism: SCRAM-SHA-256
    security_protocol: SASL_SSL
    sasl_plain_username: {username}
    sasl_plain_password: {password}
```

# Docker
```shell
mkdir sipc
pushd sipc
curl "https://gist.githubusercontent.com/xh-dev/3359450fd15f843016cc6f0babd8bfc0/raw/685d5b057fdba4024fc3b90b5c85673bae34107d/Dockerfile" -O
docker build -t sipc:latest .
```
