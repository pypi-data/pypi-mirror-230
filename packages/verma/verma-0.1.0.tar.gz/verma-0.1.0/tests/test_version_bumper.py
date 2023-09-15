from verma.core.enums import BumpLevel
from verma.core.functions import bump_version_by_level


def test_bumps_patch_version():
    current_version = 'v0.0.0'
    expected_version = 'v0.0.1'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.PATCH,
        prefix='v'
    )

    assert new_version == expected_version


def test_bumps_patch_version_when_it_has_minor():
    current_version = 'v0.1.0'
    expected_version = 'v0.1.1'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.PATCH,
        prefix='v'
    )

    assert new_version == expected_version


def test_bumps_minor_version():
    current_version = 'v0.0.0'
    expected_version = 'v0.1.0'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.MINOR,
        prefix='v'
    )

    assert new_version == expected_version


def test_bumps_minor_version_resets_minor():
    current_version = 'v0.0.12'
    expected_version = 'v0.1.0'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.MINOR,
        prefix='v'
    )

    assert new_version == expected_version


def test_bumps_minor_version_resets_minor_doesnt_affect_major():
    current_version = 'v2.11.12'
    expected_version = 'v2.12.0'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.MINOR,
        prefix='v'
    )

    assert new_version == expected_version


def test_bumps_major_version_resets_minor_and_patch():
    current_version = 'v1.11.12'
    expected_version = 'v2.0.0'

    new_version = bump_version_by_level(
        current_version=current_version,
        bump_level=BumpLevel.MAJOR,
        prefix='v'
    )

    assert new_version == expected_version
