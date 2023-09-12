#!/bin/bash

set -e
set -u

includedir=../src/assorthead/include
mkdir -p $includedir
transplant_headers() {
    local src=$1
    dest=$includedir/$(basename $src)
    rm -rf $dest
    cp -r sources/$src $dest
}

# Simple fetching, when a submodule can be directly added and the
# header files are directly available from the repository.

mkdir -p sources
fetch_simple() {
    local name=$1
    local url=$2
    local version=$3

    if [ ! -e sources/$name ]
    then
        git clone $url sources/$name
    else
        cd sources/$name
        git fetch --all
        git checkout $version
        cd -
    fi
}

fetch_simple aarand https://github.com/LTLA/aarand v1.0.1
transplant_headers aarand/include/aarand 

fetch_simple powerit https://github.com/LTLA/powerit v1.0.0
transplant_headers powerit/include/powerit

fetch_simple kmeans https://github.com/LTLA/CppKmeans v2.0.0
transplant_headers kmeans/include/kmeans

fetch_simple byteme https://github.com/LTLA/byteme v1.0.1
transplant_headers byteme/include/byteme

fetch_simple tatami https://github.com/tatami-inc/tatami v2.1.2
transplant_headers tatami/include/tatami

fetch_simple weightedlowess https://github.com/LTLA/CppWeightedLowess v1.0.1
transplant_headers weightedlowess/include/WeightedLowess

fetch_simple umappp https://github.com/LTLA/umappp f2928b3018e9dc374fbe4553769f899e575e2f14
transplant_headers umappp/include/umappp

fetch_simple qdtsne https://github.com/LTLA/qdtsne c18897e65ed28cb9c2768ec1edd6a9c1d2f20103
transplant_headers qdtsne/include/qdtsne

fetch_simple irlba https://github.com/LTLA/CppIrlba 15d6399fc2c9c2ed4755fa0baef373c086fdedd1
transplant_headers irlba/include/irlba

fetch_simple eigen https://gitlab.com/libeigen/eigen 3.4.0
transplant_headers eigen/Eigen

fetch_simple singlepp https://github.com/LTLA/singlepp 1d9869c3f050521a12b3151c89bc41906bf093e0
transplant_headers singlepp/include/singlepp

fetch_simple scran https://github.com/LTLA/libscran 1bb7cd7f2898073f40005086c740316fe5d7442e
transplant_headers scran/include/scran

fetch_simple mnncorrect https://github.com/LTLA/CppMnnCorrect 5ba5c790f01b3a676420892151791786dfb0a8d6
transplant_headers mnncorrect/include/mnncorrect

# Fetch + CMake, when a repository requires a CMake configuration
# to reorganize the headers into the right locations for consumption.
# This also handles transitive dependencies.

fetch_cmake() {
    local name=$1
    local url=$2
    local version=$3

    fetch_simple $name $url $version

    cd sources/$name
    if [ ! -e build ]
    then
        cmake -S . -B build
    fi
    cd -
}

fetch_cmake knncolle https://github.com/LTLA/knncolle 3ad6b8cdbd281d78c77390d5a6ded4513bdf3860
transplant_headers knncolle/include/knncolle
transplant_headers knncolle/build/_deps/annoy-build/include/annoy
transplant_headers knncolle/build/_deps/hnswlib-src/hnswlib
