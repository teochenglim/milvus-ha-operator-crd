"""Simple Milvus client to test connectivity and basic operations."""

from pymilvus import MilvusClient

MILVUS_URI = "http://localhost:19530"
COLLECTION = "test_collection"
DIM = 128


def main():
    client = MilvusClient(uri=MILVUS_URI)

    # Check server version
    version = client.get_server_version()
    print(f"Milvus server version: {version}")

    # Drop collection if it exists
    if client.has_collection(COLLECTION):
        client.drop_collection(COLLECTION)
        print(f"Dropped existing collection: {COLLECTION}")

    # Create collection
    client.create_collection(collection_name=COLLECTION, dimension=DIM)
    print(f"Created collection: {COLLECTION}")

    # Insert test data
    import numpy as np

    vectors = np.random.rand(10, DIM).tolist()
    data = [
        {"id": i, "vector": vectors[i], "text": f"document {i}"}
        for i in range(10)
    ]
    result = client.insert(collection_name=COLLECTION, data=data)
    print(f"Inserted {result['insert_count']} records")

    # Search
    query_vector = np.random.rand(1, DIM).tolist()
    results = client.search(
        collection_name=COLLECTION,
        data=query_vector,
        limit=3,
        output_fields=["text"],
    )
    print(f"Search results ({len(results[0])} hits):")
    for hit in results[0]:
        print(f"  id={hit['id']}, distance={hit['distance']:.4f}, text={hit['entity']['text']}")

    # Cleanup
    client.drop_collection(COLLECTION)
    print(f"Cleaned up collection: {COLLECTION}")
    print("All tests passed!")


if __name__ == "__main__":
    main()
