from pollination.ladybug.translate import EpwToWea, EpwToDdy, WeaToConstant
from queenbee.plugin.function import Function


def test_epw_to_wea():
    function = EpwToWea().queenbee
    assert function.name == 'epw-to-wea'
    assert isinstance(function, Function)


def test_epw_to_ddy():
    function = EpwToDdy().queenbee
    assert function.name == 'epw-to-ddy'
    assert isinstance(function, Function)


def test_wea_to_constant():
    function = WeaToConstant().queenbee
    assert function.name == 'wea-to-constant'
    assert isinstance(function, Function)
