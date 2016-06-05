#!/bin/bash

# Determine release version (increment revision number only).
version=$(grep version setup.py | cut -d\' -f2)
echo "Current version: ${version}"
release_version=${version/%${version##*.}/$((${version##*.}+1))}
echo "Release version: ${release_version}"

# Add the version, commit to master and push.
sed -i "" "s/${version}/${release_version}/" setup.py
git add setup.py
git commit -m "[ci skip] Bump version"
git push origin master

# Create the release.
#git tag -a ${release_version} -m "Version ${release_version}"
#git push origin refs/tags/${release_version}
#curl -s -X POST -H "Authorization: Basic amRnaWxsZXNwaWU5MTpjMmM5NTdlODc2MGQxNDlkNDUwM2MxNDBiNWY1ZWRlYWVmMGM5NTc2" -H "Accept: application/vnd.github.v3+json" -H "Content-Type: application/json" -d '{"tag_name": "'${release_version}'"}' "https://api.github.com/repos/jdgillespie91/twads/releases"
