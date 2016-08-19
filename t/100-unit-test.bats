load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup() { source bin/ckssh; }

@test "unit test mode" {
    assert_equal "$?" 0
}

@test 'meaning_of_life' {
    assert_equal $(meaning_of_life) 42
}

@test 'find_config_for nonexistent' {
    run find_config_for nobody_I_know
    assert_failure
    assert_output ''
}

@test 'find_config_for bob' {
}
