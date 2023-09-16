#!/bin/bash -x

exec mlflow server --artifacts-destination="s3://${ARTIFACT_BUCKET}" \