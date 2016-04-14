#/bin/bash
. t/test-lib.sh

echo "1..1"

start_test 'Check usage return value'
test_equal hello hello
test_equal 123 123
end_test
