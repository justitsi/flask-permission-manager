#!/bin/sh
cd /project/src
gunicorn wsgi:app -w 4 --threads 8 -b 0.0.0.0:8082
