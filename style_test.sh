#!/usr/bin/env bash
# E402 module level import not at top of file
# E501 Line too long
pycodestyle *.py --ignore=E402,E501
