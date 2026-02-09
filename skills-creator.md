basharsheikh@AAA:/mnt/d/TODO_APP/skills/TODO/TODOCHATBOT$ docker build -f Dockerfile.frontend -t todo-frontend:phase4 .
[+] Building 41670.7s (10/10) FINISHED                        docker:default
 => [internal] load build definition from Dockerfile.frontend           9.3s 
 => => transferring dockerfile: 423B                                    1.9s 
 => [internal] load metadata for docker.io/library/node:20-alpine     131.2s 
 => [auth] library/node:pull token for registry-1.docker.io             0.0s 
 => [internal] load .dockerignore                                       2.5s 
 => => transferring context: 1.73kB                                     0.5s 
 => [1/5] FROM docker.io/library/node:20-alpine@sha256:3960ed74dfe320a  0.0s 
 => [internal] load build context                                    6127.1s 
 => => transferring context: 3.75MB                                  6076.8s 
 => CACHED [2/5] WORKDIR /app                                           0.0s 
 => [3/5] COPY ./frontend .                                         34974.6s 
 => [4/5] RUN npm install                                             303.3s 
 => ERROR [5/5] RUN npm run build                                      69.0s 
------
 > [5/5] RUN npm run build:
31.06
31.06 > frontend@0.1.0 build
31.06 > next build
31.06
61.42   Downloading swc package @next/swc-linux-x64-gnu... to /root/.cache/next-swc
65.18 unhandledRejection TypeError: fetch failed
65.18     at ignore-listed frames {
65.18   [cause]: Error: getaddrinfo ENOTFOUND registry.npmjs.org
65.18       at ignore-listed frames {
65.18     errno: -3008,
65.18     code: 'ENOTFOUND',
65.18     syscall: 'getaddrinfo',
65.18     hostname: 'registry.npmjs.org'
65.18   }
65.18 }
------
Dockerfile.frontend:14
--------------------
  12 |
  13 |     # Build Next.js application
  14 | >>> RUN npm run build
  15 |
  16 |     # Expose port 3000
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c npm run build" did not complete successfully: exit code: 1