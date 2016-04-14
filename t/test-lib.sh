#!/bin/bash

cd $(dirname $0)/..
mkdir -p tmp
PATH=$(cd $(dirname $0)/.. && /bin/pwd):$PATH

#----------------------------------------------------------------------

CURRENT_TEST_NUMBER=0
CURRENT_TEST_NAME=

start_test() {
    CURRENT_TEST_NUMBER=$(expr $CURRENT_TEST_NUMBER + 1)
    CURRENT_TEST_NAME="$*"
    ENCOUNTERED_FAILURE=false
}

end_test() {
    $ENCOUNTERED_FAILURE && echo -n 'not '
    echo ok $CURRENT_TEST_NUMBER - "$CURRENT_TEST_NAME" $*
}

fail_test() {
    ENCOUNTERED_FAILURE=true
}

test_equal() {
    local expected="$1" actual="$2"
    local not=''

    [ -z "$3" ] || {
        not=not
        echo "# Extra arguments passed to test_equal."
        return
    }

    [ "$expected" == "$actual" ] || {
        fail_test
        echo "# Expected: '$expected'"
        echo "#   Actual: '$actual'"
    }
    return 0
}
