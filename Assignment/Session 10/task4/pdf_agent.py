# ============================================
# Task 4: PDF Agent using LlamaIndex
# File: pdf_agent.py
# ============================================

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load PDF documents from "data" folder
documents = SimpleDirectoryReader("data").load_data()

# Create searchable index
index = VectorStoreIndex.from_documents(documents)

# Query engine
query_engine = index.as_query_engine()

print("====== IPL PDF AI Agent ======")

question = input("Ask a question: ")

response = query_engine.query(question)

print("\nAnswer:")
print(response)