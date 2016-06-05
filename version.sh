#!/bin/bash

travis_build_dir="/home/travis/build/jdgillespie91/twads"
setup_file="${travis_build_dir}/setup.py"

# Determine release version (increment revision number only).
version=$(grep version "${setup_file}" | cut -d\' -f2)
echo "Current version: ${version}"
release_version=${version/%${version##*.}/$((${version##*.}+1))}
echo "Release version: ${release_version}"

echo "DEBUG: ${setup_file}"
echo "DEBUG: $(ls "${setup_file}")"

# Add the version, commit to master and push.
sed -i "s/${version}/${release_version}/" "${setup_file}"

# Git stuff
cd ${travis_build_dir}

echo "DEBUG: Setting user"
git config user.email "jdgillespie91@gmail.com"
git config user.name "Jake Gillespie"
echo "DEBUG: $(git config --get user.email)"
echo "DEBUG: $(git config --get user.name)"

echo "DEBUG: First status"
git status
echo "DEBUG: Add"
git add setup.py
echo "DEBUG: Second status"
git status
echo "DEBUG: Commit"
git commit -m "[ci skip] Bump version"
echo "DEBUG: URL"
echo "DEBUG: $(git remote show origin)"
echo "DEBUG: Changing URL"
git remote set-url origin "https://15dee39ff8dc11de98cc7170ef085245c7123154@github.com/jdgillespie91/twads.git"
echo "DEBUGi: Push"
git push origin master

# Create the release.
#git tag -a ${release_version} -m "Version ${release_version}"
#git push origin refs/tags/${release_version}
#curl -s -X POST -H "Authorization: Basic amRnaWxsZXNwaWU5MTpjMmM5NTdlODc2MGQxNDlkNDUwM2MxNDBiNWY1ZWRlYWVmMGM5NTc2" -H "Accept: application/vnd.github.v3+json" -H "Content-Type: application/json" -d '{"tag_name": "'${release_version}'"}' "https://api.github.com/repos/jdgillespie91/twads/releases"
