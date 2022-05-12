set -u

# This script will be run after getting the health codes
# `$AKM_PATH` and `$XCK_PATH` will be expanded to the full path
scp $AKM_PATH user@host:health-code/
scp $XCK_PATH user@host:health-code/
