#!/bin/sh
cp -n .env.example .env

docker compose up --build
