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
cat ${setup_file}
sed -i "s/${version}/${release_version}/" "${setup_file}"
cat ${setup_file}
cd ${travis_build_dir}
git add setup.py
git commit -m "[ci skip] Bump version"
git push origin master

# Create the release.
#git tag -a ${release_version} -m "Version ${release_version}"
#git push origin refs/tags/${release_version}
#curl -s -X POST -H "Authorization: Basic amRnaWxsZXNwaWU5MTpjMmM5NTdlODc2MGQxNDlkNDUwM2MxNDBiNWY1ZWRlYWVmMGM5NTc2" -H "Accept: application/vnd.github.v3+json" -H "Content-Type: application/json" -d '{"tag_name": "'${release_version}'"}' "https://api.github.com/repos/jdgillespie91/twads/releases"
