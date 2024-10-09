#!/bin/bash
echo "Building Docker Image"
export VERSION="ca:0.5.0"
docker build -t $VERSION .
echo "Built Docker Image : $VERSION"