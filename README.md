## Images

| Component | Image |
|-----------|-------|
| milvus-operator | `milvusdb/milvus-operator:v1.3.5` |
| milvus | `milvusdb/milvus:v2.6.0` |
| etcd | `docker.io/milvusdb/etcd:3.5.25-r1` |
| rustfs | `rustfs/rustfs:latest` |
| attu (UI) | `zilliz/attu:v2.6` |

## Setup

```bash
curl https://raw.githubusercontent.com/zilliztech/milvus-operator/main/deploy/manifests/deployment.yaml > deployment.yaml

curl https://raw.githubusercontent.com/zilliztech/milvus-operator/main/config/samples/milvus_cluster_woodpecker.yaml > milvus_cluster_woodpecker.yaml

```