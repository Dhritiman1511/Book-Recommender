#!/bin/bash
gunicorn -b 0.0.0.0:10000 app:app