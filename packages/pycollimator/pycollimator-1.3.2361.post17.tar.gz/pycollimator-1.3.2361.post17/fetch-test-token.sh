#!/bin/bash

set -e
cd `dirname $0`

function do_exec {
  >&2 echo "$ $@"
  "$@"
}

function do_echo {
  echo -e "\033[1;32m$@\033[0m"
}

function die {
  echo -e "\033[1;31m$@\033[0m"
  exit 1
}

USERNAME="test-group-1"
SECRETNAME="$USERNAME-clerk-password"
SECRETSDIR="secrets"

do_exec mkdir -p "$SECRETSDIR"

if [ "$PYCOLLIMATOR_SECRET_TEST_TOKEN" != "" ] ; then
  do_echo "Found secret in environment!"
  echo "$PYCOLLIMATOR_SECRET_TEST_TOKEN" > "$SECRETSDIR/token.txt"
else
  do_echo "Fetching secret token from SecretsManager: $SECRETNAME"
  if [ "$AWS_SECRET_ACCESS_KEY" = "" ] ; then
    die "This script must be ran with AWS credentials. Try this:\n\n  aws-vault exec your.id -- $0 $@\n"
  fi
  do_exec aws secretsmanager get-secret-value --secret-id $SECRETNAME --query SecretString --output text | jq -r ".token" > "$SECRETSDIR/token.txt"
fi
