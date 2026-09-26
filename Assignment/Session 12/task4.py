# ============================================
# Task 4: IPL PDF Question Answer Agent
# ============================================

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load PDF from "data" folder
documents = SimpleDirectoryReader("data").load_data()

# Create searchable index
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

print("===== IPL Match PDF Agent =====")

question = input("Ask a question: ")

response = query_engine.query(question)

print("\nAnswer:")
print(response)