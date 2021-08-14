#!/usr/bin/env bash

for file_name in index.html index.js style.css; do
    aws s3 cp "${file_name}" s3://arobogo.hu
done
