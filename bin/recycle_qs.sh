#!/bin/bash


# brew install mercury2269/homebrew-tap/sqsmover

echo $0

move() {
    sqsmover \
        -s $1 -d $2
}

move candidate-dead-letter-queue candidate-sync-queue
move committee-dead-letter-queue committee-sync-queue

move  fec-datasync-resources-FilingF1SDLQueue-6KS74XVIGDU0 fec-f1s-queue
move fec-datasync-resources-FilingSBDLQueue-SA7F6Q1JG2PR fec-sb-queue
move fec-datasync-resources-FilingSEDLQueue-171C68TG5U42I fec-se-queue

move fec-datasync-resources-FinancialSummaryDLQueue-6DOO5LC0QXR6 fec-financialsummary-queue
