from egse.system import get_module_location


def test_get_version_installed():
    from egse.version import get_version_installed

    assert get_version_installed('cgse').startswith('202')
    assert 'cgse' in get_version_installed('cgse').lower()

def test_get_version_from_git():
    from egse.version import get_version_from_git

    version, n_commits, git_hash = get_version_from_git().split('-')

    assert "CGSE" in version
    assert int(n_commits) >= 0
    assert git_hash.startswith('g')

def test_get_version_from_settings():
    from egse.version import VERSION, get_version_from_settings

    assert "CGSE" in VERSION
    assert "CGSE" in get_version_from_settings("Common-EGSE")
    assert "CGSE" in get_version_from_settings("Common-EGSE", location=get_module_location('egse'))
