import pytest
from captcha.detect import rotate_detect, notch_detect

@pytest.mark.parametrize(
    "x,c,expected",
    [
        (uint32(0xAABBCCDD), 1, uint16(0xBBCC)),
    ],
)
def test_rotate_(x, c, expected):
    result = sub42(x, c)

    assert result == expected


