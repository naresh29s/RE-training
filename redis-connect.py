import redis

server_west = redis.Redis(host='crdbtestdb-cluster2.api.34.105.62.27.nip.io',
                    port=443,
                    ssl=True,
                    ssl_cert_reqs='required',
                    ssl_ca_certs='proxy_cert_west.pem')

server_east = redis.Redis(host='crdbtestdb-cluster1.api.35.237.241.25.nip.io',
                    port=443,
                    ssl=True,
                    ssl_cert_reqs='required',
                    ssl_ca_certs='proxy_cert_east.pem')

print("Getting key from West region : 'mykey', 'Hello from Python!'")

server_west.set('mykey', 'Hello from Python!')
value = server_east.get('mykey') 
print("Getting key from East region : "+str(value))

server_west.zadd('vehicles', {'car' : 0})
server_west.zadd('vehicles', {'bike' : 0})
vehicles = server_east.zrange('vehicles', 0, -1)
print("Getting key from East region : " +str(vehicles))
