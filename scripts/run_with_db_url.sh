IPADDR=`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dcp-db-1`
DATABASE_URL=postgresql://postgres:postgres@${IPADDR}:5432/postgres python3 $@
