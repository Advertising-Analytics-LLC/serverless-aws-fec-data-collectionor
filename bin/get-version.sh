#!/bin/bash


get_version() {
    version="v0.0.1"
    git_describe_tag=$(git describe --always --dirty --match 'NOT A TAG')
    export version_tag="${version}-${git_describe_tag}"
    echo "${version}-${git_describe_tag}"
}
