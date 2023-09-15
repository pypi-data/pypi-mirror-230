import logging
import os
import sys
from pathlib import Path

import click
import git
import invoke
import rich

from egse.system import chdir

THIS_FILE_LOCATION = Path(__file__).parent

# The ROOT_PROJECT_FOLDER is the location where the Common-EGSE was installed.
# For development installations, this is where the git repository was cloned,
# for the operational system, this is usually '/cgse', but should match the
# PLATO_INSTALL_LOCATION environment variable in any case.

ROOT_PROJECT_FOLDER = THIS_FILE_LOCATION / "../.."

MODULE_LOGGER = logging.getLogger("egse.scripts")


class DirtyRepoError(Exception):
    pass


class GitCommandError(Exception):
    pass


def check_and_report_dirty_repo():
    repo = git.Repo(Path.cwd())

    if dirty := repo.is_dirty(untracked_files=False):
        rich.print("You have uncommitted changes, unable to install the Common-EGSE.")

        for item in repo.index.diff(None):
            rich.print(f"  [red]Modified: {item.a_path}")

        rich.print("Stash or submit your changes to GitHub.")

        raise DirtyRepoError()


def run_shell_command(cmd: str, hide: bool = True, warn: bool = True):
    response = invoke.run(cmd, hide=hide, warn=warn)
    rich.print(f"Executing '{response.command}'...")
    if response.return_code:
        MODULE_LOGGER.info(f"{response.stdout}")
        MODULE_LOGGER.error(f"{response.stderr}")
        raise GitCommandError()
    return response


def is_operational_install(location: str):
    # location can be the following:
    #
    #   * root folder where Common-EGSE is installed, e.g. /cgse/lib/python
    #   * the actual 'egg' folder where Common-EGSE is installed,
    #     e.g. /cgse/lib/python/Common_EGSE-2021.3_SRON_RC37-py3.8.egg

    rich.print(f"{location=}")

    if ".egg" in location:
        return True

    candidates = [path for path in os.listdir(location) if path.startswith("Common_EGSE")]

    rich.print(f"{candidates=}")

    if candidates and candidates[0].endswith(".egg"):
        return True

    # add other tests here that might indicate operational install

    return False


@click.group()
def cli():
    pass


@cli.command()
@click.option("--tag", help="The Release number to install.")
def ops(tag=None):
    """
    Update the Common-EGSE on the operational machine. An operational installation is different
    from a developer installation. There is no virtual environment and the all required Python
    packages, including the Common-EGSE are installed at a specific location. The installation
    process makes use of the following environment variables:

      * PLATO_COMMON_EGSE_PATH: the location of the plato-common-egse repository on your machine, e.g., '~/git/plato-common-egse'

      * PLATO_INSTALL_LOCATION: the location where the packages shall be installed, usually '/cgse'

    Don't update the operational system without a tag.

    The following commands will be executed:

      * git fetch updates

      * git checkout tags/<tag> -b <tag>-branch

      * python -m pip uninstall Common-EGSE

      * python setup.py install --force --home=$PLATO_INSTALL_LOCATION

    You will need to manually restart the core services as root on the egse-server:

      * systemctl restart log_cs cm_cs sm_cs pm_cs dyn_cs

    NOTE: This command only works on an installation with setuptools (not a development
          installation). The installation must have been done in the location set by the
          environment variable PLATO_INSTALL_LOCATION.

    Args:
        tag: the tag that needs to be used for the update.

    """

    try:
        plato_install_location = os.environ["PLATO_INSTALL_LOCATION"]
        MODULE_LOGGER.info(f"{plato_install_location=}")
    except KeyError:
        rich.print(
            "[red]On an operational system, the PLATO_INSTALL_LOCATION environment variable must "
            "be set.[/]\n"
            "Please set this to the root folder of the installation, usually [default]'/cgse'."
        )
        return

    if not Path(plato_install_location).exists():
        rich.print(
            f"[orange3]I didn't find the '{plato_install_location}' location on your system.[/]\n"
            "Please check if the PLATO_INSTALL_LOCATION is set to the correct folder."
        )
        return

    try:
        plato_cgse_location = os.environ["PLATO_COMMON_EGSE_PATH"]
        MODULE_LOGGER.info(f"{plato_cgse_location=}")
    except KeyError:
        rich.print(
            "[red]On an operational system, the PLATO_COMMON_EGSE_PATH environment variable must "
            "be set.[/]\nPlease set this to the root folder of the cloned repository, "
            "usually [default]'~/git/plato-common-egse'."
        )
        return

    with chdir(plato_cgse_location):
        rich.print("Updating plato-common-egse...")

        try:
            run_shell_command("git fetch updates")
            run_shell_command("git checkout develop")
        except GitCommandError:
            return

        try:
            check_and_report_dirty_repo()
        except DirtyRepoError:
            return

        if tag:
            try:
                run_shell_command(f"git checkout tags/{tag} -b {tag}-branch")
                response = run_shell_command(f"{sys.executable} -m pip show Common-EGSE | grep Location")
                location = response.stdout.split(":")[1].strip()
            except GitCommandError:
                return
            except IndexError as exc:
                rich.print(f"[red]IndexError: {exc!s}[/red]")
                return

            do_uninstall = True
            if not is_operational_install(location):
                print(
                    "It looks like your are not running a production environment, "
                    "or you have a different kind of installation. "
                )
                response = input("Is this a first-time installation? [y/n] ")

                if response.upper() == "Y":
                    do_uninstall = False
                else:
                    return

            try:
                if do_uninstall:
                    run_shell_command(f"{sys.executable} -m pip uninstall Common-EGSE", hide=False)
                run_shell_command(f"{sys.executable} setup.py install --force --home={plato_install_location}")
            except GitCommandError:
                return
        else:
            # git rev-list --tags --timestamp --no-walk | sort -nr | head -n1 | cut -f 2 -d ' ' | xargs git describe --contains
            rich.print("Usage: update_cgse ops --tag=<tag name>")
            rc = invoke.run("git describe --tags --abbrev=0", hide="stdout")
            rich.print(f"The latest tag name is '{rc.stdout.strip()}'.")
            return

        rich.print(
            "To complete the installation process, perform the following actions:\n\n"
            "On the egse-client:\n"
            "  * stop all device control servers from the PM GUI\n"
            "On the egse-server:\n"
            "  * run (in the root folder of plato-common-egse): invoke stop-core-egse\n"
            "  * the core services should automatically be re-started by systemd\n"
            "  * (if not, run (in the root folder of plato-common-egse): invoke start-core-egse)\n"
            "  * Alternatively, you can run: systemctl restart log_cs cm_cs sm_cs pm_cs syn_cs\n"
            "    (it will be no guaranteed that the processes are started in the correct order, though)"
        )


@cli.command()
def develop():
    """
    Update the Common-EGSE on a develop machine.

    The following commands will be executed in the background:

      * git fetch updates

      * git rebase updates/develop

      * python3 -m pip install -e .

    """

    with chdir(ROOT_PROJECT_FOLDER):
        rich.print("Updating plato-common-egse development environment.")

        try:
            check_and_report_dirty_repo()
        except DirtyRepoError:
            return

        try:
            run_shell_command("git fetch updates")
            run_shell_command("git checkout develop")
            run_shell_command("git rebase updates/develop")
            run_shell_command(f"{sys.executable} setup.py develop")
            run_shell_command(f"{sys.executable} setup.py egg_info")
            response = run_shell_command(f"{sys.executable} -m egse.version")
        except GitCommandError:
            return

        release = response.tail("stdout").split("\n")[-1]

        try:
            response = run_shell_command("git describe --tags --long")
            tag = response.stdout.strip().split("-")

            # The tag format is:
            #   * the annotated tag
            #   * the number of commits since the tag
            #   * abbreviated commit name (starts with the letter 'g')

            number_of_commits = tag[-2]
            bare_tag = "-".join(tag[:-2])

        except GitCommandError:
            return

        rich.print(f"{release.strip()}")
        if number_of_commits != 0:
            rich.print(f"Number of commits since {bare_tag}: {number_of_commits}")


if __name__ == "__main__":
    cli()
