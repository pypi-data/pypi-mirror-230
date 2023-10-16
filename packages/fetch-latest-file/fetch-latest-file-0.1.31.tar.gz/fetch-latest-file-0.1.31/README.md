# fetch-latest-file

## installing

```bash
pip3 install fetch-latest-file
fetch install-completion
```

## configuration

```bash

mkdir -p ~/.fetch_latest_file

echo <EOF
[source1]
host = <hostname>
destination = output_filepath
match = regex expression
path = search path on host

[source1]
host = <hostname>
destination = output_filepath
match = regex expression
path = search path on host

EOF > ~/.fetch_latest_file/config1
```
