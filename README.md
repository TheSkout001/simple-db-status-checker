simple database status checker, for [uptime kuma](https://github.com/louislam/uptime-kuma) push monitors

currently supporting only mongodb and mariadb




env variables:
> MONGO_URI *\
> MARIADB_USER *\
> MARIADB_PASSWORD *\
> MARIADB_HOST *\
> MARIADB_PORT (default: 3306)\
> \
> MONGO_HEALTHCHECK_URL *\
> MARIADB_HEALTHCHECK_URL *\
> \
> HEALTHCHECK_INTERVAL (default: 60)\
> \
> \* - required

\
sample docker-compose.yaml:
```
services:
  simple-db-status-checker:
    image: "ghcr.io/theskout001/simple-db-status-checker:latest"
    container_name: simple-db-status-checker
    restart: always
    environment: 
      - MONGO_URI=mongodb://mongodb_username:mongodb_pass@127.0.0.1:27017/
      - MARIADB_USER=CHANGEME
      - MARIADB_PASSWORD=CHANGEME
      - MARIADB_HOST=127.0.0.1
      - MONGO_HEALTHCHECK_URL=https://your_uptime-kuma_instance.aaa/api/push/ivcfgzftoxtduc
      - MARIADB_HEALTHCHECK_URL=https://your_uptime-kuma_instance.aaa/api/push/wdaktkoxafuozb
```
