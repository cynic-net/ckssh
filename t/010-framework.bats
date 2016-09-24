load 'ckssh-test-lib'

@test "pass" {
    assert true
    refute false
}

test_run_function() { echo test_run_function; return 17; }

@test "run for functions" {
    run test_run_function
    assert_failure 17
    assert_output test_run_function
}
