#!/bin/sh
set -eu

gosu mongodb mongod --bind_ip 127.0.0.1 --dbpath /data/db &
mongod_pid=$!
app_pid=

cleanup() {
    if [ -n "$app_pid" ]; then
        kill -TERM "$app_pid" 2>/dev/null || true
    fi
    kill -TERM "$mongod_pid" 2>/dev/null || true
    wait "$mongod_pid" 2>/dev/null || true
}

trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

attempt=0
until python -c 'from pymongo import MongoClient; MongoClient(serverSelectionTimeoutMS=1000).admin.command("ping")' >/dev/null 2>&1; do
    if ! kill -0 "$mongod_pid" 2>/dev/null; then
        echo "MongoDB exited before becoming ready" >&2
        wait "$mongod_pid" || true
        exit 1
    fi
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then
        echo "MongoDB did not become ready within 30 seconds" >&2
        exit 1
    fi
    sleep 1
done

"$@" &
app_pid=$!
if wait "$app_pid"; then
    exit 0
else
    exit $?
fi
