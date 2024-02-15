#!/bin/bash

# mongo
cat test-data/algorithm.json | docker exec -i mongo mongoimport --db=rap --collection algorithm --legacy mongodb://localhost
