load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; source bin/ckssh; }
teardown() { teardown_bats_tmp; }

@test "unit test mode" {
    assert_equal "$?" 0
}

@test "expand_tilde" {
    assert_equal "$(expand_tilde 'ab/cd'    )"  'ab/cd'
    assert_equal "$(expand_tilde '~'        )"  '~'
    assert_equal "$(expand_tilde '~/'       )"  "$HOME/"
    assert_equal "$(expand_tilde '~root'    )"  '~root'
}

@test 'strip_userat' {
    assert_equal "$(strip_userat foo)"          foo
    assert_equal "$(strip_userat foo@bar)"      bar
    assert_equal "$(strip_userat foo@bar@bam)"  bar@bam
}
