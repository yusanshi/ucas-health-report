set -u

# This script will be run after getting the health codes
# `$AKM_PATH`, `$XCK_PATH` and `$HSM_PATH`(if not empty) will be expanded to the full path
scp $AKM_PATH user@host:health-code/
scp $XCK_PATH user@host:health-code/
# only run if `$HSM_PATH` is not empty
[[ !  -z  $HSM_PATH  ]] && scp $HSM_PATH user@host:health-code/
