load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup() { source bin/ckssh; }

@test "unit test mode" {
    assert_equal "$?" 0
}

@test 'meaning_of_life' {
    assert_equal $(meaning_of_life) 42
}
