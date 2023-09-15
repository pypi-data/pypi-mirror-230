#!/bin/bash
# ================================================================================
# replace these values with the values you need for your build
# ================================================================================
org="<<org>>"
app="<<app>>"
packager="<<author>>"
version="0.1"
release="000001"
summary="<<short_desc>>"
license="<<org>>-<<app>>"      # Manditory see https://fedoraproject.org/wiki/Licensing:Main#GPL_Compatibility_Matrix for some good info
url=""          # URL is optional and can be left blank or commented out
group=""        # Group is optional and can be left blank or commented out
vendor=""       # Vendor is optional and can be left blank or commented out otherwise place your organization description here.
# 
# Place description between the lines of hyphens
description="
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
"
# ================================================================================



# assign a variable with a temp description file name.
temp_description_file=$(mktemp)

# write description data to temp file. Will get imported by the rpmspec
echo "$description" > $temp_description_file

if [[ "$url" == "" ]]; then url="--"; fi
if [[ "$group" == "" ]]; then group="--"; fi
if [[ "$vendor" == "" ]]; then vendor="--"; fi

rm -rf ~/rpmbuild/RPMS/x86_64/*

# The command below runs rpmbuild and passes your values into the build
rpmbuild \
        --define "_org $org " \
        --define "_app $app " \
        --define "_packager $packager " \
        --define "_version $version" \
        --define "_release $release" \
        --define "_summary $summary" \
        --define "_description_file $temp_description_file" \
        --define "_license $license" \
        --define "_url $url" \
        --define "_group $group" \
        --define "_vendor $vendor" \
        --build-in-place \
        --target x86_64 \
        -bb server_config/centos8/rpm.spec

build_status=$?

# remove the temp description file
rm -f $temp_description_file

copy_rpm=$1
if [[ $copy_rpm != "do_not_copy" ]]; then
        #
        if [[ ! -d ./rpmbuild ]]; then
                mkdir ./rpmbuild
        fi

        if [[ $build_status -eq 0 ]]; then
                cp -f ~/rpmbuild/RPMS/x86_64/* ./rpmbuild/ 
        fi
fi

if [[ $build_status -ne 0 ]]; then
	echo "Error building RPM, exit status $build_status"
	exit $build_status
fi