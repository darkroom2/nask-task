#!/usr/bin/env bash

set -e

yapf -i -r nask_task_app/
flake8 nask_task_app/
coverage run -m unittest discover
coverage report
