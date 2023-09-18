# Copyright 2023 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from tempfile import NamedTemporaryFile

from portmodlib.portmod import Group, Person, parse_package_metadata


def test_metadata():
    with NamedTemporaryFile("w", delete=False) as file:
        print(
            """
maintainer: me@example.org
use:
    test: description
    other: foo
upstream:
    maintainer: Someone <foo@example.org>
""",
            file=file,
        )

    metadata = parse_package_metadata(file.name)

    assert metadata.use == {"test": "description", "other": "foo"}
    assert isinstance(metadata.maintainer, Person)
    # Not recognized as the email if there is just an email
    assert str(metadata.maintainer) == metadata.maintainer.name == "me@example.org"

    assert metadata.upstream
    assert isinstance(metadata.upstream.maintainer, Person)
    assert str(metadata.upstream.maintainer) == "Someone <foo@example.org>"
    assert metadata.upstream.maintainer.name == "Someone"
    assert metadata.upstream.maintainer.email == "foo@example.org"
    os.remove(file.name)


def test_metadata_maintainer_nonstring():
    with NamedTemporaryFile("w", delete=False) as file:
        print(
            """
maintainer:
    name: Someone
    email: foo@example.org
    desc: This is a test

upstream:
    maintainer:
    - name: Someone
    - Someone else
""",
            file=file,
        )

    metadata = parse_package_metadata(file.name)

    assert isinstance(metadata.maintainer, Person)
    assert metadata.maintainer.name == "Someone"
    assert metadata.maintainer.email == "foo@example.org"
    assert metadata.maintainer.desc == "This is a test"
    assert str(metadata.maintainer) == "Someone <foo@example.org>"

    assert metadata.upstream
    assert isinstance(metadata.upstream.maintainer, list)
    assert all(isinstance(person, Person) for person in metadata.upstream.maintainer)
    assert list(map(str, metadata.upstream.maintainer)) == ["Someone", "Someone else"]
    os.remove(file.name)


def test_metadata_maintainer_group():
    with NamedTemporaryFile("w", delete=False) as file:
        print(
            """
maintainer:
    group: Some group
""",
            file=file,
        )

    metadata = parse_package_metadata(file.name)

    assert isinstance(metadata.maintainer, Group)
    assert metadata.maintainer.group == "Some group"
    os.remove(file.name)
