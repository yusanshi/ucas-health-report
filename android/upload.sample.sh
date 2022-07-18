set -u
set -e

# This script will be run after getting the health codes
# `$XCK_PATH` will be expanded to the full path
scp $XCK_PATH user@host:health-code/

exit 0
