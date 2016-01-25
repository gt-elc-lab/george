#!/bin/bash
cd "$(dirname "$0")"
pwd
export PRODUCTION=TRUE
python -m tasks.crawl_task
