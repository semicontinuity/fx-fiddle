#!/usr/bin/env bash

jseparate-after() {
    local FIELD=$1
    local VALUE=$2
    local SEP_FIELD=${3:-separator}

    if [[ -z "$FIELD" || -z "$VALUE" ]]; then
        echo "Usage: jseparate-after <field> <value> [separator_field]" >&2
        echo "Example: echo '[...]' | jseparate-after \"status\" \"completed\"" >&2
        return 1
    fi

    jq -s -c --arg fld "$FIELD" --arg val "$VALUE" --arg sep_fld "$SEP_FIELD" '
        foreach .[] as $i (
            { found: false };
            if .found or ($i[$fld] == $val)
            then { curr: $i, found: true }
            else { curr: $i, found: false }
            end;
            if .found and ($i[$fld] != $val)
            then $i + {($sep_fld): 1}
            else $i + {($sep_fld): 0}
            end
        )
    '
}

jseparate-after "$@"
