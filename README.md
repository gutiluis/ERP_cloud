# how it works:
cp .env.example .env
# first make mysql db with docker
docker compose up -d db # name is erp_db from the docker-compose.yml file
# second check mysql db connection with docker




#
docker compose up --build api









--
# how to test mysql docker connection after downloading the image and container:
docker ps
docker images
docker compose ps












---
# make typescript configuration file from CLI commands
# https://www.typescriptlang.org/docs/handbook/compiler-options.html
tsc --init # first make npm init -y

---
### TESTING MODULES:
### FRONTEND testing
### How to run eslint:
```
npx eslint
```
---
### Frontend unit test with: VITEST
Files to test src/main/index.ts:
### to test src/main/index.ts. run from the root project
- npm install -D vitest
- touch src/main/index.test.ts
---
### VITEST
test each module first for frontend with vite mock
