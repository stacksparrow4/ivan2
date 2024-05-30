#!/bin/bash

./build_image.sh && \
kubectl apply -k . && \
kubectl rollout restart deployment/ivan2