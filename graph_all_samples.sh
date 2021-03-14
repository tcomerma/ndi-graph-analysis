#!/bin/bash

find samples/*.txt -exec python3 ndi-graph-analysis.py -f {} \;