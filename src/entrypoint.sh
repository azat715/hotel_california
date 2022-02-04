#!/bin/sh
/code/wait-for-it.sh db:5432 -t 30 -- echo "run db"

uvicorn hotel_california.entrypoints.app.main:app --host 0.0.0.0 --port 8000 
