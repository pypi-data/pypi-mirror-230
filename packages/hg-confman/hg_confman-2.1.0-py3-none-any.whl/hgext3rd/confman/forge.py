import collections
import os
import shutil
import tarfile
import tempfile
import urllib.request

# https://github.com/orus-io/elm-spa/archive/refs/heads/master.zip
# https://github.com/orus-io/elm-spa/archive/refs/tags/1.2.0.zip
# https://github.com/orus-io/elm-spa/archive/refs/heads/example-cleanup.zip
# https://github.com/orus-io/elm-spa/archive/8a97e89fbc2933f3f53037bae53d730d7e496df2.zip


TRACK_CSET = "cset"
TRACK_BRANCH = "branch"
TRACK_TAG = "tag"


def github_vars(pulluri, track):
    return {
        "track": track,
        "path": pulluri.path.lstrip("/"),
        "name": pulluri.path.split("/")[-1],
    }


def gitlab_vars(pulluri, track):
    token_env_name = "CONFMAN_CI_" + pulluri.host.upper().replace(".", "_") + "_TOKEN"
    return {
        "track": track,
        "path": pulluri.path.lstrip("/"),
        "name": pulluri.path.split("/")[-1],
        "token": "?private_token=" + os.environ.get(token_env_name)
        if token_env_name in os.environ
        else "",
    }


known_forges = {
    "github.com": "github",
    "gitlab.com": "gitlab",
    "foss.heptapod.net": "heptapod",
}


registry = {
    "github": {
        "vars": github_vars,
        "git.cset": {
            "url": "https://github.com/%(path)s/archive/%(track)s.tar.gz",
            "prefix": "%(name)s-%(track)s",
        },
        "git.branch": {
            "url": "https://github.com/%(path)s/archive/refs/heads/%(track)s.tar.gz",
            "prefix": "%(name)s-%(track)s",
        },
        "git.tag": {
            "url": "https://github.com/%(path)s/archive/refs/tags/%(track)s.tar.gz",
            "prefix": "%(name)s-%(track)s",
        },
    },
    "gitlab": {
        "vars": gitlab_vars,
        "git.cset": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "git.branch": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "git.tag": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
    },
    "heptapod": {
        "vars": gitlab_vars,
        "hg.cset": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "hg.branch": {
            "url": "https://orus.io/%(path)s/-/archive/branch/%(track)s/%(name)s-branch-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-branch-%(track)s",
        },
        "hg.tag": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "git.cset": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "git.branch": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
        "git.tag": {
            "url": "https://orus.io/%(path)s/-/archive/%(track)s/%(name)s-%(track)s.tar.gz%(token)s",
            "prefix": "%(name)s-%(track)s",
        },
    },
}


URI = collections.namedtuple(
    'URI', ["vcs", "scheme", "host", "path", "user", "password"]
)


def parse_uri(uri):
    vcs = "hg"
    if uri.endswith(".git"):
        vcs = "git"
        uri = uri.removesuffix(".git")
    u = urllib.parse.urlparse(uri)
    if u.netloc != "":
        return URI(vcs, u.scheme, u.netloc, u.path, u.username, u.password)
    if vcs == "git":
        # assume the uri matches "user@host:path
        host = uri.split("@")[1].split(":")[0]
        path = uri.split(":")[1]
        return URI("git", "git", host, path)
    raise RuntimeError("invalid uri: " + uri)


def checkout(ui, forgetypes, section, rev, secconf):
    pulluri = parse_uri(secconf["pulluri"])
    forgetype = forgetypes.get(pulluri.host) or known_forges.get(pulluri.host)
    if forgetype is None:
        raise RuntimeError(
            "could not determine '%s' forge type. Please complete the '[:confman:forgetypes]' section of your .hgconf file"
            % pulluri.host,
        )
    forge = registry.get(forgetype)
    if not forge:
        raise RuntimeError("unknown forge type: %s" % forgetype)

    vcs = "hg"
    if secconf["pulluri"].endswith(".git"):
        vcs = "git"

    forge_vars = forge['vars'](pulluri, rev)

    # poke the forge type (bb, gh, gl, heptapod)
    for k in (TRACK_CSET, TRACK_TAG, TRACK_BRANCH):
        url = forge["%s.%s" % (vcs, k)]["url"] % forge_vars
        prefix = forge["%s.%s" % (vcs, k)]["prefix"] % forge_vars

        try:
            ui.write("fetching %s...\n" % (url.split("?")[0]))
            req = urllib.request.Request(
                url,
            )
            f = urllib.request.urlopen(req)
            if f.headers.get("Content-Type") not in (
                "application/octet-stream",
                "application/x-gzip",
            ):
                ui.write("not a .gz stream (%s)\n" % (f.headers.get("Content-Type")))
                continue
            with tempfile.NamedTemporaryFile(
                "w+b",
                prefix="confman-" + section.replace("/", "-") + "-",
                suffix=".tar.gz",
                delete=False,
            ) as tmp:
                while True:
                    b = f.read(1024 * 1024)
                    if len(b) == 0:
                        break
                    tmp.write(b)
                tmp.flush()
                tmp.seek(0)

                tar = tarfile.open(mode='r:gz', fileobj=tmp)
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar.extractall(path=tmpdir)
                    if not os.path.exists(os.path.dirname(secconf["layout"])):
                        os.makedirs(os.path.dirname(secconf["layout"]))
                    if os.path.exists(secconf["layout"]):
                        shutil.rmtree(secconf["layout"])
                    shutil.move(os.path.join(tmpdir, prefix), secconf["layout"])
            ui.write(" -> extracted to %s\n" % (secconf["layout"]))
            break
        except urllib.error.URLError as e:
            ui.write("failed: error was: %s\n" % (e))
