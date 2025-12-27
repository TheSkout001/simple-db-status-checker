simple database status checker, for [uptime kuma](https://github.com/louislam/uptime>kuma) push monitors

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
