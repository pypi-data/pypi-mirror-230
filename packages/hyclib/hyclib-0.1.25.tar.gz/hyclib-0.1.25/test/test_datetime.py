import datetime

import pytest

import hyclib as lib

@pytest.mark.parametrize(
    'td, fmt, expected',
    [
        (
            datetime.timedelta(days=2, hours=1, minutes=5, seconds=12),
            '%Hh%Ss',
            '49h312s',
        ),
        (
            datetime.timedelta(weeks=2, days=4, hours=100, minutes=5, seconds=12, milliseconds=150, microseconds=5),
            '%w weeks %d days %H:%M:%S.%f',
            '3 weeks 1 days 04:05:12.150005',
        ),
        (
            datetime.timedelta(days=-4, hours=10, minutes=5, seconds=12, milliseconds=150, microseconds=5),
            '%d days, %H:%M:%S.%f',
            None,
        ),
    ],
)      
def test_strftime(td, fmt, expected):
    if expected is None:
        expected = str(td)
        
    output = lib.datetime.strftime(td, fmt)

    assert output == expected