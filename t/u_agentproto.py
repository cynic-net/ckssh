' Unit Tests: SSH agent protocol '

from    io import BytesIO
from    binascii import unhexlify
import  pytest
from    ckssh import (
            read_agentproto_int,
            SSHAgentProtoError, read_agentproto_idcomments,
            fetch_keynames,
        )

@pytest.mark.parametrize('expected, input', (
    (7,             b'\x07'),
    (255,           b'\xff'),
    (2**16-2,       b'\xff\xfe'),
    (0x01020304,    b'\x01\x02\x03\x04'),
    (2**32-3,       b'\xff\xff\xff\xfd'),
    (2**64-4,       b'\xff\xff\xff\xff\xff\xff\xff\xfc'),
    ))
def test_read_agentproto_int(expected, input):
    assert expected == read_agentproto_int(BytesIO(input), len(input))

def test_ssh2_ids_answer_decode_0():
    answer0 = (
        b'\x00\x00\x00\x05'     # message length
        b'\x0c'                 # SSH2_AGENT_IDENTITIES_ANSWER
        b'\x00\x00\x00\x00'     # identities count: 0
    )
    assert [] == read_agentproto_idcomments(BytesIO(bytes(answer0)))

def test_ssh2_ids_answer_decode_2():
    answer2 = (
        b''
        b'\0\0\0\5'     # message length
        b'\x0C'         # SSH2_AGENT_IDENTITIES_ANSWER
        b'\0\0\0\2'     # identities count: 2

        b'\0\0\0\1'     # 1st answer blob length: 1
        b'\x7E'
        b'\0\0\0\3'     # 1st answer comment length: 3
        b'foo'

        b'\0\0\0\0'     # 2nd answer blob length: 0
        b''
        b'\0\0\0\7'     # 2nd answer comment length: 7
        b'bar baz'
    )
    assert ['foo', 'bar baz'] \
        == read_agentproto_idcomments(BytesIO(bytes(answer2)))

@pytest.mark.parametrize('badmsg', (
    '',
    '00000001',     # no response type
    '0000000102',   # bad response type
    '000000020C',   # bad length
    ))
def test_ssh2_ids_answer_decode_err(badmsg):
    bs = unhexlify(badmsg)  # Convert printable test param to bytes
    with pytest.raises(SSHAgentProtoError):
        read_agentproto_idcomments(BytesIO(bs))

def test_fetch_keynames():
    assert None is fetch_keynames({})   # No socket name in environment
    assert None is fetch_keynames(
        { 'SSH_AUTH_SOCK': '/this path/had better not exist' })
    # XXX no tests yet for actually talking to an auth server
