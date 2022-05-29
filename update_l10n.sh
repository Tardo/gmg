#!/bin/sh
# Automatizes POT file generation and existent PO update for translation

##### Script Configuration #####
COPYRIGHT_HOLDER="Alexandre Diaz"
MSGID_BUGS_ADDR="https://github.com/Tardo/gmg/issues"
CHARSET="UTF-8"

POT=messages.pot
CFG=babel.cfg
L10NDIR="./translations/"

# Get pybabel path in different distros
PYBABEL=$(whereis -b pybabel | awk '{print $2}')
################################

##### Initial Verification #####
if [ ! -d $L10NDIR ]; then
	echo "Error: $L10NDIR not found. Are you running this script from root dir?"
	exit 1
fi

if [ ! -r $CFG ]; then
    echo "Error: $CFG not found."
    exit 1
fi

if [ ! -x $PYBABEL ]; then
        echo "Error: pybabel not found. Please make sure it is installed."
        exit 1
fi
#################################

# TODO: Add verification for jinja installed
# Generates POT files
$PYBABEL extract --charset=$CHARSET --mapping=$CFG --output=$POT   \
    --no-wrap --sort-by-file --msgid-bugs-address=$MSGID_BUGS_ADDR \
    --copyright-holder="$COPYRIGHT_HOLDER"  "$L10NDIR/.."            || exit 1

# Updates existent PO files
$PYBABEL update --input-file=$POT --output-dir="$L10NDIR" --previous || exit 1

# Compiles existent PO files, generating MO files
$PYBABEL compile --directory="$L10NDIR" --statistics                 || exit 1
