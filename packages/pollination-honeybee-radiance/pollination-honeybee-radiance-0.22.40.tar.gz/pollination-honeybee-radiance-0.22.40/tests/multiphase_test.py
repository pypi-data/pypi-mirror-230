from pollination.honeybee_radiance.multiphase import ViewMatrix, FluxTransfer
from queenbee.plugin.function import Function


def test_view_mtx():
    function = ViewMatrix().queenbee
    assert function.name == 'view-matrix'
    assert isinstance(function, Function)


def test_flux_transfer():
    function = FluxTransfer().queenbee
    assert function.name == 'flux-transfer'
    assert isinstance(function, Function)
