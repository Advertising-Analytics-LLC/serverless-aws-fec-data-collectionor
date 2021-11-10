#!/bin/bash


run_lambda() {
	outfile="$(date +%F_%H-%M-%S)-${1}-out.txt"

	echo "running ${1}, writing to outfile ${outfile}"
	aws lambda invoke \
		--function-name $1 \
		$outfile
}

while read lambda
do
	run_lambda $lambda
done <<EOF
serverless-aws-python3-fec-datasync-dev-CandidateSync
serverless-aws-python3-fec-datasync-dev-CommitteeSync
serverless-aws-python3-fec-datasync-dev-FilingSync
EOF
