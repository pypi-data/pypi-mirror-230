from pollination.honeybee_radiance.grid import SplitGrid, MergeFiles, \
    SplitGridFolder, MergeFolderData, MirrorGrid, RadiantEnclosureInfo
from queenbee.plugin.function import Function


def test_split_grid():
    function = SplitGrid().queenbee
    assert function.name == 'split-grid'
    assert isinstance(function, Function)


def test_merge_files():
    function = MergeFiles().queenbee
    assert function.name == 'merge-files'
    assert isinstance(function, Function)


def test_split_folder():
    function = SplitGridFolder().queenbee
    assert function.name == 'split-grid-folder'
    assert isinstance(function, Function)


def test_merge_folder():
    function = MergeFolderData().queenbee
    assert function.name == 'merge-folder-data'
    assert isinstance(function, Function)


def test_mirror_grid():
    function = MirrorGrid().queenbee
    assert function.name == 'mirror-grid'
    assert isinstance(function, Function)


def test_radiant_enclosure_info():
    function = RadiantEnclosureInfo().queenbee
    assert function.name == 'radiant-enclosure-info'
    assert isinstance(function, Function)
