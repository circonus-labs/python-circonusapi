set -e

export CIRCONUS_CONFIG=./test_config.ini

python test_circonusapi.py

if python -c 'import sys; sys.exit(not sys.version_info.major == 3 )'
then
  # python3 only tests
  python test_circonusdata.py
fi
