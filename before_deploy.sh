#!/bin/bash

function setup {
    # Travis build directory.
    cd "/home/travis/build/jdgillespie91/twads"

    # Set up git to allow pushing from this repo.
    git config user.email "jdgillespie91@gmail.com"
    git config user.name "Jake Gillespie"
    git remote set-url origin "https://${TWADS_TOKEN}@github.com/jdgillespie91/twads.git"
}

function bump_version {
    # Determine release by incrementing patch number of current version.
    version=$(grep version "setup.py" | cut -d\' -f2)
    release_version=${version/%${version##*.}/$((${version##*.}+1))}

    echo "current version: ${version}"
    echo "release version: ${release_version}"

    sed -i "s/${version}/${release_version}/" "setup.py"

    if [ $? -eq 0 ]; then
        echo "version bumped successfully"
    fi
}

function push_version_to_github {
    # We need to prevent the build here since we're pushing to master.
    git add setup.py
    git commit -m "[ci skip] Bump version"
    git branch bump-version
    git checkout master
    git merge bump-version
    git push origin master
}

function push_release_to_github {
    curl -s -X POST -H "Authorization: Basic ${TWADS_TOKEN}" -H "Accept: application/vnd.github.v3+json" -H "Content-Type: application/json" -d '{"tag_name": "'${release_version}'"}' "https://api.github.com/repos/jdgillespie91/twads/releases"
}

function main {
    setup
    bump_version
    push_version_to_github
    push_release_to_github
}

main
