#!/bin/bash
set -e
set -u

VERSION=$(grep "^version" metadata.txt| cut -d= -f2)

# TODO: THREEDITOOLBOX_ARTIFACTS_KEY should be set as env variable in the travis UI.
# TODO: TRAVIS_BRANCH is set automatically by travis
ARTIFACT=ThreeDiToolbox.${VERSION}.zip
PROJECT=ThreeDiToolbox

# Rename generated ThreeDiToolbox.zip to include version number.
cp ThreeDiToolbox.zip ${ARTIFACT}

curl -X POST \
     --retry 3 \
     -H "Content-Type: multipart/form-data" \
     -F key=${THREEDITOOLBOX_ARTIFACTS_KEY} \
     -F artifact=@${ARTIFACT} \
     -F branch=${TRAVIS_BRANCH} \
     https://artifacts.lizard.net/upload/${PROJECT}/
