# Milvus HA

Milvus vector database cluster deployment on Kubernetes using the Milvus Operator, with RustFS as S3-compatible object storage and Woodpecker as the message stream.

https://milvus.io/docs/install_cluster-milvusoperator.md?tab=kubectl

## Architecture

```
                        +-----------+
                        |   Attu    |
                        |  (WebUI)  |
                        +-----+-----+
                              |
                        +-----+-----+
                        |   Proxy   |
                        +-----+-----+
                              |
          +----------+--------+--------+-----------+
          |          |                 |            |
     +----+----+ +---+-----+  +-------+---+  +----+------+
     | MixCoord| | DataNode|  | QueryNode |  |Streaming  |
     |         | |         |  |           |  |   Node    |
     +---------+ +---------+  +-----------+  +-----------+
          |          |              |              |
     +----+----------+--------------+--------------+----+
     |                    etcd                          |
     +--------------------------------------------------+
     |                   RustFS                         |
     +--------------------------------------------------+
```

## Images

| Component | Image |
|-----------|-------|
| milvus-operator | `milvusdb/milvus-operator:v1.3.5` |
| milvus | `milvusdb/milvus:v2.6.0` |
| etcd | `docker.io/milvusdb/etcd:3.5.25-r1` |
| rustfs | `rustfs/rustfs:latest` |
| attu (UI) | `zilliz/attu:v2.6` |

## Project Structure

```
.
├── k8s/                                    # Kubernetes manifests
│   ├── milvus-operator-crd.yaml            # Custom Resource Definitions
│   ├── milvus-operator-serviceaccount.yaml  # ServiceAccount
│   ├── milvus-operator-role.yaml           # RBAC Role (namespace-scoped)
│   ├── milvus-operator-rolebinding.yaml    # RBAC RoleBinding
│   ├── milvus-operator-service.yaml        # Operator services (metrics + webhook)
│   ├── milvus-operator-deployment.yaml     # Operator deployment
│   ├── milvus-rustfs-secret.yaml           # RustFS credentials
│   ├── milvus-rustfs-statefulset.yaml      # RustFS StatefulSet + Service
│   └── milvus-attu-deployment.yaml         # Attu Web UI
├── milvus-cluster.yaml                     # Milvus cluster CR
├── client/                                 # Python test client (uv)
│   ├── pyproject.toml
│   └── test_milvus.py
└── original/                               # Upstream reference manifests
```

## Prerequisites

- Kubernetes cluster with `kubectl` context set to the target namespace
- No ClusterRole permissions required (all RBAC is namespace-scoped)

## Deploy

### 1. Operator

Apply manifests in order:

```bash
kubectl apply -f k8s/milvus-operator-crd.yaml
kubectl apply -f k8s/milvus-operator-serviceaccount.yaml
kubectl apply -f k8s/milvus-operator-role.yaml
kubectl apply -f k8s/milvus-operator-rolebinding.yaml
kubectl apply -f k8s/milvus-operator-service.yaml
kubectl apply -f k8s/milvus-operator-deployment.yaml
```

### 2. Storage (RustFS)

```bash
kubectl apply -f k8s/milvus-rustfs-secret.yaml
kubectl apply -f k8s/milvus-rustfs-statefulset.yaml
```

### 3. Milvus Cluster

```bash
kubectl apply -f milvus-cluster.yaml
```

The operator will provision etcd (3 replicas) and all Milvus components automatically.

### 4. Web UI (Attu)

```bash
kubectl apply -f k8s/milvus-attu-deployment.yaml
kubectl port-forward svc/milvus-attu 3000:3000
# Open http://localhost:3000
```

## Verify

```bash
# Check all conditions are True
kubectl get milvus milvus -o jsonpath='{range .status.conditions[*]}{.type}: {.status}{"\n"}{end}'

# Expected output:
# MilvusReady: True
# MilvusUpdated: True
# EtcdReady: True
# StorageReady: True
# MsgStreamReady: True
```

## Test Client

```bash
kubectl port-forward svc/milvus-milvus 19530:19530 &
cd client
uv run test_milvus.py
```

## Teardown

```bash
# 1. Delete Milvus cluster CR (operator removes milvus components)
kubectl delete -f milvus-cluster.yaml

# 2. Delete etcd (operator deploys it via helm with Retain policy, so it survives CR deletion)
kubectl delete statefulset milvus-etcd
kubectl delete svc milvus-etcd milvus-etcd-headless
kubectl delete secret -l name=milvus-etcd,owner=helm
kubectl delete pvc data-milvus-etcd-0 data-milvus-etcd-1 data-milvus-etcd-2

# 3. Delete all k8s/ resources (operator, rustfs, attu) and rustfs PVC
kubectl delete -f k8s/
kubectl delete pvc data-rustfs-0
```

## Notes

- The operator runs with `-watch-namespace default` to work with namespace-scoped Roles instead of ClusterRoles
- RustFS replaces MinIO as S3-compatible object storage
- Woodpecker is used as the message stream (no Kafka/Pulsar needed)
- Default RustFS credentials are `rustfsadmin/rustfsadmin` - update `k8s/milvus-rustfs-secret.yaml` for production

## Reference

- [Milvus Operator](https://github.com/zilliztech/milvus-operator)
- [RustFS](https://github.com/rustfs/rustfs)
- [Attu - Milvus Web UI](https://github.com/zilliztech/attu)
