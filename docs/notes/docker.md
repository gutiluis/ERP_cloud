# Docker Notes

## Persistency

Volume mounts are great for persistently storing data for containers, and for sharing data between containers.

Bind mounts, on the other hand, are for sharing data between a container and the host.

https://docs.docker.com/engine/containers/run/

## Multi-stage builds

Multi-stage builds allow multiple `FROM` stages to be used in a single Dockerfile. Build dependencies can remain in an intermediate stage while only the required runtime artifacts are copied into the final image.

Reference:

https://docs.docker.com/build/building/multi-stage/
