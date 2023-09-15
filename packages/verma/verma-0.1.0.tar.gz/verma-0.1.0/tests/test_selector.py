import pytest

from verma.core import BumpLevelSelectorBuilder
from verma.core.enums import BumpLevel


@pytest.fixture
def selector():
    selector = (
        BumpLevelSelectorBuilder()
            .use_major_patterns(['BREAKING CHANGES:'])
            .use_patch_patterns(['^fix:'])
            .use_minor_patterns(['^feat:'])
            .build()
    )

    return selector


def test_it_selects_patch(selector):
    message = 'fix: Some addition\n'

    level = selector.select(message=message)

    assert level == BumpLevel.PATCH


def test_it_selects_patch(selector):
    message = 'fix: Some addition\n'

    level = selector.select(message=message)

    assert level == BumpLevel.PATCH


def test_it_selects_minor(selector):
    message = 'feat: Some addition\n'

    level = selector.select(message=message)

    assert level == BumpLevel.MINOR


def test_it_selects_major_over_patch(selector):
    message = 'fix: Some addition\n\nBREAKING CHANGES: '

    level = selector.select(message=message)

    assert level == BumpLevel.MAJOR


def test_it_selects_major_over_minor(selector):
    message = 'feat: Some addition\n\nBREAKING CHANGES: '

    level = selector.select(message=message)

    assert level == BumpLevel.MAJOR