#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/9/11 18:43
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

docker run -d --name=es \
  --restart=always \
  -e "discovery.type=single-node" \
  --memory=1g --memory-swap=1g --ulimit memlock=-1 \
  -p 9200:9200 -p 9300:9300 \
  -v /root/data/es/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
  -v /root/data/es/data:/usr/share/elasticsearch/data \
  -v /root/data/es/logs:/usr/share/elasticsearch/logs \
  -v /root/data/es/plugins:/usr/share/elasticsearch/plugins \
  elasticsearch:8.9.0


docker container kill es && docker rm es

docker logs -f --tail=100 es


docker exec -it es /bin/bash
