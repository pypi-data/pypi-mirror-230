from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from transformers import AutoTokenizer, AutoModel

# Initialize an InMemoryDocumentStore
document_store = InMemoryDocumentStore()

# Write a sample document to the store
document_store.write_documents(
    [
        {
            "text": "Hello, world! This is a sample document for Haystack with Hugging Face embeddings.",
            "meta": {"name": "sample_doc"},
        }
    ]
)

# Load a pre-trained model and tokenizer from Hugging Face's model hub
model_name = "deepset/sentence_bert"
model = AutoModel.from_pretrained(model_name)

# Initialize an EmbeddingRetriever with the pre-trained model and tokenizer
retriever = EmbeddingRetriever(document_store=document_store, embedding_model=model)

# Update the embeddings in the document store
document_store.update_embeddings(retriever=retriever)

# Fetch a document using the retriever
query = "Find me a document with Hugging Face embeddings"
results = retriever.retrieve(query)

# Print the results
for result in results:
    print(result)
