"""
This module provides convenience functions to use resources in your code without
the need to specify an absolute path or try to locate the resources in your local
installation (which is time-consuming, error-prone, and introduces quite some
redundancy).

Resources can be files of different format that are distributed together with the
source code, e.g.

    * image data
    * icons
    * YAML files
    * binary files, e.g. dynamic libraries
    * style files for GUI applications
    * calibration files distributed with the source code

Each of the resources have a fixed location within the source tree and is identified
with a resource identifier. There are a number of default identifier that are defined
as follows:

    * `icons`: located in the sub-folder 'icons'
    * `images`: located in the sub-folder 'images'
    * `lib`: located in sub-folder 'lib'

Resource locations are determined during startup at a number of predefined
locations for the following resource identifiers:

    * from known hardcoded folder names, e.g. 'images', 'icons', and 'lib'.

Resources can be accessed from the code without specifying the absolute pathname,
using a `:/resource_od/` that is known by the resource module. A wildcard can be
introduces after the `resource_id` to indicate the resource is in one of the
sub-directories.

Example usage:
    * get_resource(":/icons/open-document.png")
    * get_resource(":/styles/dark.qss")
    * get_resource(":/lib/*/EtherSpaceLink_v34_86.dylib")

A new `resource_id` can be added with the `add_resource_id()` function, specifying a
resource_id string and location. When the `force=True` keyword is given, an existing
resource_id can be changed.

Alternatives

The `egse.config` module has a number of alternatives for locating files and resources.

    * find_file(..) and find_files(..)
    * find_dir(..) and find_dirs(..)
    * get_resource_dirs()
    * get_resource_path()

The functions for finding files and directories are more flexible, but take more
time and effort. They are mainly used for dynamically searching for a file or
folder, not necessarily within the source code location.

The resource specific functions in the egse.config module will be deprecated when
their functionality is fully replaced by this `egse.resource` module.

"""

import logging
import re
from pathlib import Path
from typing import Dict
from typing import Union

from egse.config import find_first_occurrence_of_dir
from egse.config import find_files
from egse.exceptions import InternalError

MODULE_LOGGER = logging.getLogger(__name__)


class ResourceError(Exception):
    """Base class, raised when a resource is not defined."""


class AmbiguityError(ResourceError):
    """Raised when more than one option is possible."""


class NoSuchFileError(ResourceError):
    """Raised when no file could be found for the given resource."""


__all__ = [
    "get_resource",
    "get_resource_locations",
    "add_resource_id",
    "initialise_resources",
    "ResourceError",
    "AmbiguityError",
    "NoSuchFileError",
]

# Testing regex: https://pythex.org

PATTERN = re.compile(r"^:/(\w+)/(\*+/)?(.*)$")

DEFAULT_RESOURCES = {
    "icons": "/icons",
    "images": "/images",
    "lib": "/lib",
    "styles": "/styles",
    "data": "/data",
    "aeudata": "/aeu/arbdata",
}

resources_root = Path(__file__).parent
resources = {}

__initialised__ = False


def check_if_file_exists(filename: Union[Path, str], resource_id: str = None) -> Path:
    """
    Check if the given filename exists. If the filename exists, return the filename, else raise a
    NoSuchFileError.

    Args:
        filename (Path|str): an absolute filename
        resource_id (str): a resource identifier

    Return:
        The given filename if it exists.

    Raises:
        NoSuchFileError if the given filename doesn't exist.
    """
    filename = Path(filename)
    if filename.is_file():
        return filename

    if resource_id:
        raise NoSuchFileError(
            f"The file '{filename.name}' could not be found for the given resource '{resource_id}'")
    else:
        raise NoSuchFileError(f"The file '{filename.name}' doesn't exist.")


def contains_wildcard(filename: str):
    """
    Returns True if the filename contains a wildcard, otherwise False.
    A wildcard is an asterisk '*' or a question mark '?' character.
    """
    if '*' in filename:
        return True
    if '?' in filename:
        return True

    return False


def get_resource_locations() -> Dict[str, Path]:
    """
    Returns a dictionary of names that can be used as resource location.
    The keys are strings that are recognised as valid resource identifiers, the
    values are their actual absolute path names.
    """
    if not __initialised__:
        MODULE_LOGGER.warning("Resources have not been initialised.")

    return resources.copy()


def initialise_resources(root: Union[Path, str] = Path(__file__).parent):
    """
    Initialise the default resources.

    The argument `root` specifies the root location for the resources. If not specified,
    the location of this module is taken as the root location. So, if you have installed
    this package with `pip install`, you should give the location of your project's source
    code as the root argument.

    Args:
        root (Path|str): the root location for the resources.

    Returns:
        None.
    """
    global resources_root
    global __initialised__

    if __initialised__:
        MODULE_LOGGER.warning("Resources have already been initialised.")
        return

    resources_root = Path(root)

    #  the resources with their absolute path names

    for resource_id in DEFAULT_RESOURCES:
        folder = find_first_occurrence_of_dir(DEFAULT_RESOURCES[resource_id], root=resources_root)
        resources[resource_id] = folder

    MODULE_LOGGER.debug(f"Resources have been defined: {DEFAULT_RESOURCES=}")

    __initialised__ = True


def add_resource_id(resource_id: str, location: Union[Path, str], force=False):
    """
    Adds a resource identifier with the given location. Resources can then be specified
    using this resource id.

    The location can be an absolute or relative pathname. In the latter case an
    absolute pathname will be constructed using the resource root location that was
    given during the initialisation (calling `initialise_resources()`).

    If the resource identifier already exists, a ValueError will be raised unless
    you specify the `force=True` argument.

    Args:
        resource_id (str): a resource identifier
        location (Path|str: an absolute or relative pathname
        force (bool): force adding even if the resource_id exists

    Returns:
        ValueError if the location can not be determined.
    """
    # Check if id already exists, overwrite or raise exception?

    if resource_id in resources and force is False:
        raise ValueError(f"Resource identifier '{resource_id}' already exists.")

    # Check if location exists and is a directory.

    location = Path(location)

    if location.is_absolute() and location.is_dir():
        resources[resource_id] = location

    if not location.is_absolute():
        location = resources_root / location
        if location.is_dir():
            resources[resource_id] = location
        else:
            raise ValueError(f"Unknown location {location=}")


def get_resource(resource_locator: str) -> Path:
    """
    Returns the absolute Path for the given resource_locator. The resource_locator consists of
    a resource_id, an optional wildcard and a filename separated by a forward slash '/' and
    started by a colon ':'.

        ':/<resource_id>/[*/]<filename>'

    If the resource_locator starts with a colon ':', the name will be interpreted as a resource_id
    and filename combination and parsed as such

    If the resource_locator doesn't start with a colon ':', then the string will be interpreted as a
    Path name and returned if that path exists, otherwise a ResourceError is raised.

    The filename can contain the wildcard '*' and/or '?', however the use of a wildcard in the
    filename can still only match one unique filename. This can be useful e.g. if you know the
    filename except for one part of it like a timestamp. Used, e.g., for matching Setup files which
    are unique filenames with a timestamp.

    Args:
        resource_locator (str): a special resource name or a filename

    Returns:
        a Path with the absolute filename for the resource.

    Raises:
        ResourceError when no file could be found or the search is ambiguous.

    """
    # Try to match the special resource syntax `:/resource_id/` or `:/resource_id/*/`

    if resource_locator.startswith(':'):

        if not __initialised__:
            MODULE_LOGGER.warning("Resources have not been initialised.")

        match = PATTERN.fullmatch(resource_locator)
        resource_id = match[1]
        filename = match[3]
        try:
            resource_location = Path(resources[resource_id])
        except KeyError:
            raise ResourceError(f"Resource not defined: {resource_id}")

        # Match can be only three things
        #   - None in which case the file must be in the resource location directly
        #   - '*/' in which case the file must be in a sub-folder of the resource
        #   - '**/' to find the file in any sub-folder below the given resource

        if match[2] is None:
            if contains_wildcard(filename):
                files = list(find_files(filename, root=resource_location))

                if len(files) == 1:
                    filename = files[0]
                elif len(files) == 0:
                    raise NoSuchFileError(f"No file found that matches {filename=} for the given "
                                          f"resource '{resource_id}'.")
                else:
                    raise AmbiguityError(f"The {filename=} found {len(files)} matches for "
                                         f"the given resource '{resource_id}'.")

            return check_if_file_exists(resource_location / filename, resource_id)

        elif match[2] == "*/":
            files = list(find_files(filename, root=resource_location))

            if len(files) == 1:
                return files[0]
            elif len(files) == 0:
                raise NoSuchFileError(
                    f"The {filename=} could not be found for the given resource '{resource_id}'."
                )
            else:
                raise AmbiguityError(f"The {filename=} was found {len(files)} times for "
                                     f"the given resource '{resource_id}'.")
        elif match[2] == '**/':
            raise NotImplementedError(f"The '**' to walk the tree is not yet implemented.")
        else:
            raise InternalError(
                f"This shouldn't happen, the match is {match[2]=} for {resource_locator=}")
    else:
        return check_if_file_exists(Path(resource_locator))


initialise_resources()

if __name__ == "__main__":

    import rich
    rich.print("Default resources:")
    rich.print(get_resource_locations())
