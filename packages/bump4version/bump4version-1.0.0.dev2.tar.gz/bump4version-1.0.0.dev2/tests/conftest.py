import os
import subprocess
from functools import partial

import pytest


@pytest.fixture(scope="session")
def subprocess_env():
    env = os.environ.copy()
    env["HGENCODING"] = "utf-8"
    return env


@pytest.fixture(scope="session")
def call(subprocess_env):
    return partial(subprocess.call, env=subprocess_env, shell=True)


@pytest.fixture(scope="session")
def check_call(subprocess_env):
    return partial(subprocess.check_call, env=subprocess_env)


@pytest.fixture(scope="session")
def check_output(subprocess_env):
    return partial(subprocess.check_output, env=subprocess_env)


@pytest.fixture(scope="session")
def run(subprocess_env):
    return partial(subprocess.run, env=subprocess_env)


class VCS:
    GIT = "git"
    MERCURIAL = "hg"


@pytest.fixture(scope="session")
def check_vcs_presence(call):
    def checker(vcs: str) -> None:
        if call(f"{vcs} version") != 0:
            pytest.xfail(reason=f"{vcs} is not installed.", run=False)
    return checker


@pytest.fixture(scope="session", params=[VCS.GIT, VCS.MERCURIAL])
def vcs(request, check_vcs_presence):
    """Return all supported VCS systems (git, hg)."""
    vcs = request.param
    check_vcs_presence(vcs=vcs)
    return vcs


@pytest.fixture(scope="session")
def git(check_vcs_presence):
    """Return git as VCS (not hg)."""
    check_vcs_presence(vcs=VCS.GIT)
    return VCS.GIT
