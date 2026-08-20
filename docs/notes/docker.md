# Docker Notes

## Multi-stage builds

Multi-stage builds allow multiple `FROM` stages to be used in a single Dockerfile. Build dependencies can remain in an intermediate stage while only the required runtime artifacts are copied into the final image.

Reference:

https://docs.docker.com/build/building/multi-stage/
