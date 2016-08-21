load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup() {
    HOME="$BATS_TEST_DIRNAME/test_home"
    source bin/ckssh
}

@test "unit test mode" {
    assert_equal "$?" 0
}

@test 'meaning_of_life' {
    assert_equal $(meaning_of_life) 42
}

@test 'find_config_for no config file' {
    HOME="$BATS_TEST_DIRNAME/nonexistent"
    run find_config_for bob
    assert_failure 2
    assert_output ''
}

@test 'find_config_for unknown host' {
    run find_config_for nobody_I_know
    assert_failure 1
    assert_output ''
}

@test 'find_config_for bob' {
    run find_config_for bob
    assert_success
    assert_output <<___
CK_Compartment cjs@cynic.net
Host 192.168.1.1
X11Fowarding yes
___
}
