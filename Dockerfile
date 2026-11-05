# Two stages. The first installs dependencies with build tools available;
# the second copies only the result, so compilers, headers and the uv cache
# never reach the image that runs in production. Fewer packages in the final
# image means fewer CVEs to answer for, and a smaller thing to pull on every
# deploy.

# ---------------------------------------------------------------- builder
# Pinned to an exact patch version and a digest-stable base. "3.12-slim"
# alone is a moving tag: the image would change under you on a later build
# and a deployment that worked yesterday could fail today for reasons no
# commit explains.
FROM python:3.12.8-slim-bookworm AS builder

# uv copied from its own published image rather than installed with a shell
# script piped from the internet. The version is pinned for the same reason
# everything else here is.
COPY --from=ghcr.io/astral-sh/uv:0.5.14 /uv /usr/local/bin/uv

WORKDIR /build

# Only the files that describe dependencies, so this layer is cached and
# reused whenever application code changes but the lockfile does not. Most
# deploys change code, not dependencies, which makes this the difference
# between a fast build and a slow one.
COPY pyproject.toml uv.lock ./

# --frozen: install exactly what the lockfile says and fail if it is out of
#   date. A build that silently resolves a different version is a build that
#   ships something nobody reviewed.
# --no-dev: ruff and anything else in the dev group stays out of production.
# --no-install-project: the project itself is not a package here
#   (tool.uv package = false); only its dependencies are installed.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --frozen --no-dev --no-install-project


# ---------------------------------------------------------------- runtime
FROM python:3.12.8-slim-bookworm AS runtime

# Keeps Python from writing .pyc files into a read-only-ish container and
# from buffering output, which would make logs appear late or not at all
# when the process is killed.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# A non-root user, created before anything is copied. A container process
# running as root that escapes its container is root on the host; one that
# escapes as this user is not. Nothing here needs root at any point.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --no-create-home app

WORKDIR /srv/app

COPY --from=builder /opt/venv /opt/venv

# Ownership set during the copy rather than with a later chown, which would
# duplicate every file into a second layer.
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app

USER app

EXPOSE 8000

# No migrations here. See Step 70: running them from the application's own
# startup means every replica races to migrate, and a failed migration takes
# the application down with it rather than failing a deploy step that can be
# stopped and looked at.
#
# No --reload, and no --workers either: process count belongs to whatever
# runs this container, which can see how much CPU it was given. Hard-coding
# it here would be a guess made at build time about a machine that does not
# exist yet.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
