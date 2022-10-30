#!/usr/bin/env bash

set -e

yapf -i -r nask_task_app/
flake8 nask_task_app/
coverage run nask_task_app/tests/