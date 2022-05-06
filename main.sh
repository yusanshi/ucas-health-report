#!/bin/bash

set -e

source ./config.sh

mkdir -p ${SAVE_DIR}

${GENYMOTION_DIR}/player --vm-name "${DEVICE_NAME}" 1>/dev/null 2>&1 &
sleep 25

${GENYMOTION_DIR}/genymotion-shell -q -c "gps setstatus enabled"
${GENYMOTION_DIR}/genymotion-shell -q -c "gps setlatitude ${LATITUDE}"
${GENYMOTION_DIR}/genymotion-shell -q -c "gps setlongitude ${LONGITUDE}"
${GENYMOTION_DIR}/tools/adb shell "svc wifi enable"

sleep 15

AKM_PATH="${SAVE_DIR}/$(date -I)-akm.png" 
XCK_PATH="${SAVE_DIR}/$(date -I)-xck.png"

python get_health_code.py --akm_path ${AKM_PATH} --xck_path ${XCK_PATH}
python get_image_similiarity.py --first ${AKM_PATH} --second ${AKM_SAMPLE}
python get_image_similiarity.py --first ${XCK_PATH} --second ${XCK_SAMPLE}

${GENYMOTION_DIR}/player --vm-name "${DEVICE_NAME}" --poweroff


python upload_and_apply.py --akm_path ${AKM_PATH} --xck_path ${XCK_PATH}
