#!/bin/bash
cd "$(dirname "$0")"
exec poetry run python -m server.main "$@"
