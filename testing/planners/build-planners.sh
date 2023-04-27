#!/bin/bash

cd bfws && singularity build ../dual-bfws.sif dual-bfws.def && cd ..
cd lama && singularity build ../lama-first.sif lama-first.def && cd ..
cd siwr && singularity build ../siwr.sif siwr.def && cd ..
cd h-policy && singularity build ../h-policy.sif h-policy.def && cd ..