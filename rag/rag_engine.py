import os
import time
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
import hashlib
from .smart_cache import SmartCache

# Disable ChromaDB telemetry to avoid errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"

class RAGEngine:
    def __init__(self, dataset_path: str):
        self.dataset_path = os.path.abspath(dataset_path)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="threejs_docs",
            embedding_function=self.embedding_function
        )
        
        # Initialize smart cache
        self.cache = SmartCache()
        
        # Performance metrics
        self.metrics = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0
        }
    
    def index_documents(self):
        print(f"Indexing from path: {self.dataset_path}")
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)
            print(f"Created dataset directory: {self.dataset_path}")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        print(f"Walking directory: {self.dataset_path}")
        for root, dirs, files in os.walk(self.dataset_path):
            print(f"Checking directory: {root}")
            print(f"Files found: {files}")
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                
                # Handle JSONL files
                if file.endswith('.jsonl'):
                    print(f"Processing JSONL file: {file_path}")
                    try:
                        import json
                        line_count = 0
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f):
                                if line.strip():
                                    line_count += 1
                                    try:
                                        data = json.loads(line)
                                        # Extract the conversation
                                        if 'contents' in data and len(data['contents']) >= 2:
                                            user_prompt = data['contents'][0]['parts'][0]['text']
                                            model_response = data['contents'][1]['parts'][0]['text']
                                            
                                            # Combine prompt and response for better context
                                            content = f"User: {user_prompt}\n\nResponse:\n{model_response}"
                                            
                                            doc_id = hashlib.md5(f"{file_path}_{line_num}".encode()).hexdigest()
                                            documents.append(content)
                                            metadatas.append({
                                                "filename": file,
                                                "path": file_path,
                                                "line": line_num,
                                                "type": "jsonl",
                                                "prompt": user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
                                            })
                                            ids.append(doc_id)
                                    except json.JSONDecodeError as e:
                                        print(f"Error parsing JSON at line {line_num} in {file_path}: {e}")
                        print(f"Processed {line_count} lines from {file_path}, extracted {len([d for d in documents[-line_count:] if d])} documents")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                
                # Handle regular text files
                elif file.endswith(('.md', '.txt', '.js', '.jsx', '.ts', '.tsx')):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            if content.strip():
                                doc_id = hashlib.md5(file_path.encode()).hexdigest()
                                documents.append(content)
                                metadatas.append({
                                    "filename": file,
                                    "path": file_path,
                                    "type": os.path.splitext(file)[1]
                                })
                                ids.append(doc_id)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        if documents:
            # Clear existing documents by getting all ids first
            try:
                existing = self.collection.get()
                if existing['ids']:
                    self.collection.delete(ids=existing['ids'])
            except:
                pass  # Collection might be empty
            
            # Add new documents
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Indexed {len(documents)} documents")
        else:
            print("No documents found to index")
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        start_time = time.time()
        self.metrics["total_searches"] += 1
        
        # Try to get from cache first
        cached_result = self.cache.get_rag_result(query)
        if cached_result:
            results, cache_metadata = cached_result
            self.metrics["cache_hits"] += 1
            
            # Add cache metadata to results
            for doc in results:
                doc["cache_metadata"] = cache_metadata
            
            print(f"🚀 Cache hit ({cache_metadata['cache_hit']}): {cache_metadata.get('similarity', 1.0):.3f} similarity")
            return results[:k]  # Return requested number of results
        
        # Perform actual search
        print(f"🔍 Searching ChromaDB for: {query[:50]}...")
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                doc = {
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0,
                    "cache_metadata": {"cache_hit": "miss"}
                }
                documents.append(doc)
        
        # Cache the results for future use
        search_time = time.time() - start_time
        self.cache.cache_rag_result(query, documents, search_time)
        
        # Update metrics
        self.metrics["avg_search_time"] = (
            (self.metrics["avg_search_time"] * (self.metrics["total_searches"] - 1) + search_time) 
            / self.metrics["total_searches"]
        )
        
        print(f"⏱️  Search completed in {search_time:.3f}s")
        return documents
    
    def get_performance_stats(self) -> Dict:
        """Get performance and cache statistics."""
        cache_stats = self.cache.get_cache_stats()
        
        return {
            "rag_metrics": self.metrics,
            "cache_stats": cache_stats,
            "hit_rate": self.metrics["cache_hits"] / max(self.metrics["total_searches"], 1),
            "performance_improvement": {
                "avg_cached_time": cache_stats.get("avg_response_time", 0),
                "avg_search_time": self.metrics["avg_search_time"],
                "speedup_factor": self.metrics["avg_search_time"] / max(cache_stats.get("avg_response_time", 1), 0.001)
            }
        }
    
    def warm_cache(self):
        """Warm up the cache with common ThreeJS queries."""
        common_queries = [
            "create rotating cube with lighting",
            "sphere geometry with texture mapping", 
            "particle system with animation",
            "camera controls and orbit",
            "vector field visualization",
            "3D mathematical function plotting",
            "physics simulation bouncing balls",
            "wireframe geometry examples",
            "material properties and shaders",
            "scene lighting setup directional ambient"
        ]
        
        print("🔥 Warming up RAG cache...")
        for query in common_queries:
            self.search(query, k=3)
        
        self.cache.warm_cache(common_queries)