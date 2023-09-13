#!/bin/bash
MODEL_VERSION="$1"
rm model_version.txt
TAG="v$MODEL_VERSION"_"$MODEL_ENV"
COMMIT=$(git rev-parse --short HEAD)

echo "Deleting tag if it already exists: $TAG"
git tag -d $TAG
git push origin :refs/tags/$TAG
echo "Tagging commit with tag: $TAG"
git tag $TAG $COMMIT
git push origin $TAG
