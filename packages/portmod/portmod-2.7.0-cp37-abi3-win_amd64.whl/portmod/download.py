# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import logging
import os
import shutil
import urllib.parse
from base64 import b16encode, b64decode
from logging import info
from typing import AbstractSet, Callable, Dict, Iterable, List, Optional, Set

from portmod.config import get_config
from portmod.config.license import _get_pkg_license_groups
from portmod.globals import env
from portmod.io import Progress
from portmod.parsers.manifest import FileType, ManifestFile
from portmod.pybuild import Pybuild
from portmod.source import LocalHashError, SourceManifest
from portmodlib.fs import get_hash
from portmodlib.l10n import l10n
from portmodlib.portmod import directories
from portmodlib.source import HashAlg, Source
from portmodlib.usestr import use_reduce

FetchProgress = Callable[[str, int, Optional[int]], Progress]


def get_null(_filename, _start, _end) -> Progress:
    class NullProgress(Progress):
        def __init__(self):
            ...

        def update(self, *, value: Optional[int] = None):
            ...

        def done(self):
            ...

    return NullProgress()


class RemoteHashError(Exception):
    """Exception indicating an unexpected download file"""


class SourceUnfetchable(Exception):
    """Exception indicating an unexpected download file"""


def get_filename(basename: str, path: Optional[str] = None) -> str:
    """
    By default returns the location of the local cached version of the source
    file corresponding to the given name. The file may or may not exist.
    @return full path of file combined from path and basename
    """
    if not path:
        path = env.DOWNLOAD_DIR
    return os.path.join(path, basename)


def mirrorable(mod: Pybuild, enabled_use: Optional[AbstractSet[str]] = None) -> bool:
    """
    Returns whether or not a mod can be mirrored
    """
    # FIXME: Determine which sources have use requirements
    # that don't enable mirror or fetch
    if "mirror" not in mod.RESTRICT and "fetch" not in mod.RESTRICT:
        redis = _get_pkg_license_groups(mod).get("REDISTRIBUTABLE", [])

        def is_license_redis(group):
            if not group:
                # No license is considered equivalent to all-rights-reserved
                return False
            if isinstance(group, str):
                return group in redis
            if group[0] == "||":
                return any(is_license_redis(li) for li in group)

            return all(is_license_redis(li) for li in group)

        if enabled_use and is_license_redis(
            use_reduce(mod.LICENSE, enabled_use, opconvert=True)
        ):
            return True
        if not enabled_use and is_license_redis(
            use_reduce(mod.LICENSE, opconvert=True, matchall=True)
        ):
            return True

    return False


def fetchable(
    mod: Pybuild, enabled_use: AbstractSet[str] = frozenset(), matchall: bool = False
) -> List[SourceManifest]:
    """
    Returns the list of fetchable sources associated with a mod
    A source can be fetched if it is mirrorable,
    or if it has a URI
    """
    restricted = use_reduce(mod.RESTRICT, enabled_use, flat=True, matchall=matchall)
    if "fetch" in restricted:
        return []

    if "mirror" not in restricted and mirrorable(mod, enabled_use):
        return mod.get_source_manifests(enabled_use)

    can_fetch = []
    for source in mod.get_source_manifests(enabled_use):
        parsedurl = urllib.parse.urlparse(source.url)
        if parsedurl.scheme:
            can_fetch.append(source)

    return can_fetch


def progress_write(
    request,
    filepath,
    start=0,
    mode="wb",
    *,
    get_progress: FetchProgress,
    size: Optional[int] = None,
):
    bytes = start
    progress = get_progress(os.path.basename(filepath), start, size)
    with open(filepath, mode=mode) as file:
        for buf in request.iter_content(1024):
            if buf:
                file.write(buf)
                bytes += len(buf)
                progress.update(value=bytes)
    progress.done()


def get_remote_size(request):
    if "Content-Length" in request.headers:
        return int(request.headers["Content-Length"].strip())
    else:
        return None


def get_remote_hashes(request):
    header = "X-Goog-Hash"
    remote_hashes = {}

    if header in request.headers:
        for remote_hash in request.headers[header].split(", "):
            hash = remote_hash.split("=", maxsplit=1)
            remote_hashes[hash[0]] = hash[1]
        if "md5" in remote_hashes:
            remote_hashes["md5"] = (
                b16encode(b64decode(remote_hashes["md5"])).decode("utf-8").lower()
            )

    return remote_hashes


def download(
    url: str,
    dest_name: str,
    *,
    get_progress: FetchProgress = get_null,
    size: Optional[int] = None,
    hashes: Dict[HashAlg, str] = {},
    dest_path: Optional[str] = None,
    check_only: bool = False,
):
    """
    Downloads the given url to the dest_path
    """
    # Slow imports
    import requests

    info(l10n("fetching", url=url))

    if not dest_path:
        dest_path = env.DOWNLOAD_DIR

    os.makedirs(dest_path, exist_ok=True)

    # TODO: Don't hardcode timeout
    req = requests.get(url, stream=True, timeout=(5, 30))
    req.raise_for_status()

    precheck = False
    remote_size = get_remote_size(req)
    remote_hashes = get_remote_hashes(req)

    if "md5" in remote_hashes and HashAlg.MD5 in hashes:
        precheck = True
        remote_hash = remote_hashes["md5"]
        if hashes[HashAlg.MD5] != remote_hash:
            raise RemoteHashError(
                l10n(
                    "remote-hash-mismatch",
                    alg="md5",
                    hash1=hashes[HashAlg.MD5],
                    hash2=remote_hash,
                )
            )

    if remote_size is not None and size is not None and remote_size != size:
        raise RemoteHashError(
            l10n("remote-size-mismatch", our_size=size, remote_size=remote_size)
        )

    if not check_only:
        file = get_filename(dest_name, dest_path)
        progress_write(req, file, size=remote_size or size, get_progress=get_progress)

        if remote_size:
            filesize = os.path.getsize(file)
            while filesize < remote_size:
                req = requests.get(
                    url,
                    stream=True,
                    headers={"Range": "bytes=%d-" % filesize},
                    timeout=(5, 30),
                )
                progress_write(
                    req,
                    file,
                    start=filesize,
                    mode="ab",
                    size=remote_size,
                    get_progress=get_progress,
                )
                filesize = os.path.getsize(file)

        # Skip post check if we did a pre-check using a local hash
        if not precheck and "md5" in remote_hashes:
            localhash = get_hash(get_filename(dest_name), (HashAlg.MD5,))[0]
            if localhash != remote_hashes["md5"]:
                # Try again
                download(
                    url,
                    dest_name,
                    size=size,
                    hashes=hashes,
                    dest_path=dest_path,
                    get_progress=get_progress,
                )


def get_download(source: Source) -> Optional[str]:
    src = find_download(source)
    if src:
        dest = get_filename(source.name)
        if src == dest:
            return dest

        info(l10n("file-moving", src=src, dest=dest))
        shutil.move(src, dest)
        return dest
    return None


def find_download(source: Source) -> Optional[str]:
    """
    Determines if the given file is in the cache.
    The file must match both name and checksum
    @return path to donloaded file
    """

    def find_by_name(directory: str) -> Optional[str]:
        if os.path.exists(directory):
            src = os.path.join(directory, source.name)
            if os.path.exists(src) and (
                not isinstance(source, SourceManifest) or source.check_file(src)
            ):
                return src

            # If a file with spaces otherwise matches use it
            for file in os.listdir(directory):
                src = os.path.join(directory, file)
                if file.replace(" ", "_") == source.name:
                    try:
                        if not isinstance(source, SourceManifest) or source.check_file(
                            src, raise_ex=True
                        ):
                            return src
                    except LocalHashError as e:
                        logging.warning(
                            l10n(
                                "possible-local-hash-mismatch",
                                filename=file,
                                name=source.name,
                            )
                            + f": {e}"
                        )
        return None

    return (
        find_by_name(env.DOWNLOAD_DIR)
        or find_by_name(
            directories.download_dir
            or os.path.expanduser(os.path.join("~", "Downloads"))
        )
        or find_by_name(os.environ.get("DOWNLOADS", ""))
    )


def is_downloaded(mod: Pybuild, enabled_use: Set[str]) -> bool:
    """
    Returns true if all the mod's sources can be found
    """
    for source in mod.get_source_manifests(enabled_use):
        cached = find_download(source)
        if cached is None:
            return False
    return True


def download_and_check(
    url: str,
    source: SourceManifest,
    *,
    try_again: bool = True,
    get_progress: FetchProgress = get_null,
):
    download(
        url,
        source.name,
        size=source.size,
        hashes=source.hashes,
        get_progress=get_progress,
    )
    filename = get_filename(source.name)

    try:
        source.check_file(filename, raise_ex=True)
    except LocalHashError as e:
        if try_again:  # Try again once if download fails
            get_hash.cache_clear()
            logging.error(e)
            print(l10n("retrying-download", url=url))
            download_and_check(url, source, try_again=False, get_progress=get_progress)
        else:
            raise


def download_source(
    mod,
    source: Source,
    *,
    get_progress: FetchProgress = get_null,
    check_remote: bool = False,
) -> str:
    """
    Downloads the given source file.
    @return the path to the downloaded source file
    """
    # Slow import
    import requests

    cached = get_download(source)
    fetch = "fetch" not in mod.get_restrict()
    mirror = (
        "mirror" not in mod.get_restrict()
        and "fetch" not in mod.get_restrict()
        and mirrorable(mod)
    )

    if cached:
        # Download is in cache. Nothing to do.
        return cached
    elif not fetch:
        # Mod cannot be fetched and is not already in cache. abort.
        raise SourceUnfetchable(l10n("source-unfetchable", source=source))
    else:
        parsedurl = urllib.parse.urlparse(source.url)

        # Download archive
        filename = get_filename(source.name)

        def _download_source_inner(url: str):
            if isinstance(source, SourceManifest):
                if check_remote:
                    download(
                        url,
                        source.name,
                        size=source.size,
                        hashes=source.hashes,
                        check_only=True,
                    )
                else:
                    download_and_check(url, source, get_progress=get_progress)
            else:
                download(
                    url, source.name, check_only=check_remote, get_progress=get_progress
                )

        if mirror:
            PORTMOD_MIRRORS = get_config()["PORTMOD_MIRRORS"].split()
            for mirror_url in PORTMOD_MIRRORS:
                try:
                    url = urllib.parse.urljoin(mirror_url, source.name)

                    _download_source_inner(url)

                    return filename
                except requests.exceptions.HTTPError as err:
                    if parsedurl.scheme:
                        logging.info(f"{err}")
                    else:  # If there is no original source, warn instead of info
                        logging.warning(f"{err}")

        if parsedurl.scheme != "":
            _download_source_inner(source.url)

            return filename

        raise SourceUnfetchable(l10n("source-unfetchable", source=source))


def download_mod(
    mod: Pybuild,
    enabled_flags: AbstractSet[str],
    *,
    get_progress: FetchProgress = get_null,
    matchall=False,
) -> List[SourceManifest]:
    """
    Downloads missing sources for the given mod in its current USE configuration
    @return A list of paths of the sources for the mod
    """
    download_list = []
    if matchall:
        sources = mod.get_source_manifests(matchall=True)
    else:
        sources = mod.get_source_manifests(enabled_flags)

    for source in sources:
        download_source(mod, source, get_progress=get_progress)

        download_list.append(source)

    return download_list


def get_total_download_size(mods: Iterable[Pybuild]) -> int:
    """
    Returns the total size of the given mod(s) in bytes.

    args:
        mods: Mods to be measured

    returns:
        The size of the mod(s) in bytes

    """
    download_bytes: int = 0
    for mod in mods:
        manifest_file = mod.get_manifest()
        for manifest in manifest_file.entries.values():
            if (
                isinstance(manifest, ManifestFile)
                and manifest.file_type == FileType.DIST
            ):
                download_bytes += manifest.size

    return download_bytes


def get_download_size(packages: Dict[Pybuild, Set[str]]) -> float:
    """
    Returns the download size for the packages in the given configuration

    args:
        packages: A dictionary mapping each package to check to its enabled USE flags

    returns:
        The size of the downloads in MiB
    """
    download_bytes = 0
    for mod, enabled_use in packages.items():
        sources = mod.get_source_manifests(enabled_use)
        for source in sources:
            if find_download(source) is None:
                download_bytes += source.size

    return download_bytes / 1024 / 1024
