import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from datetime import datetime, timedelta
import pickle

class SmartCache:
    def __init__(self, cache_dir: str = "cache", similarity_threshold: float = 0.85):
        self.cache_dir = cache_dir
        self.similarity_threshold = similarity_threshold
        self.db_path = os.path.join(cache_dir, "cache.db")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize sentence transformer for semantic similarity
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize SQLite database
        self._init_database()
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "avg_response_time": 0,
            "learning_improvements": 0
        }
        
        # Load existing stats
        self._load_stats()
    
    def _init_database(self):
        """Initialize SQLite database for caching."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for different cache types
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                query_text TEXT,
                query_embedding BLOB,
                results BLOB,
                usage_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                avg_response_time REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash TEXT UNIQUE,
                prompt_text TEXT,
                prompt_embedding BLOB,
                context_hash TEXT,
                generated_code TEXT,
                temperature REAL,
                quality_score REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 1,
                user_feedback REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data BLOB,
                effectiveness REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON rag_cache(query_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prompt_hash ON code_cache(prompt_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_used ON rag_cache(last_used)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quality_score ON code_cache(quality_score)')
        
        conn.commit()
        conn.close()
    
    def _load_stats(self):
        """Load cache statistics from file."""
        stats_file = os.path.join(self.cache_dir, "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    self.stats.update(json.load(f))
            except:
                pass
    
    def _save_stats(self):
        """Save cache statistics to file."""
        stats_file = os.path.join(self.cache_dir, "stats.json")
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _hash_query(self, query: str) -> str:
        """Create hash for query string."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _hash_prompt(self, prompt: str, context: str = "", temperature: float = 0.7) -> str:
        """Create hash for prompt + context + temperature."""
        combined = f"{prompt.lower().strip()}|{context}|{temperature}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get sentence embedding for semantic similarity."""
        return self.embedder.encode(text)
    
    def _find_similar_rag_queries(self, query: str, query_embedding: np.ndarray, limit: int = 5) -> List[Tuple]:
        """Find similar RAG queries using semantic similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT query_hash, query_text, query_embedding, results, usage_count, success_rate
            FROM rag_cache 
            ORDER BY usage_count DESC, success_rate DESC
            LIMIT 50
        ''')
        
        candidates = []
        for row in cursor.fetchall():
            cached_embedding = pickle.loads(row[2])
            similarity = cosine_similarity([query_embedding], [cached_embedding])[0][0]
            
            if similarity >= self.similarity_threshold:
                candidates.append((similarity, row))
        
        conn.close()
        
        # Sort by similarity score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:limit]
    
    def _find_similar_code_prompts(self, prompt: str, prompt_embedding: np.ndarray, limit: int = 3) -> List[Tuple]:
        """Find similar code generation prompts using semantic similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt_hash, prompt_text, prompt_embedding, generated_code, 
                   quality_score, usage_count, user_feedback
            FROM code_cache 
            WHERE quality_score > 0.5
            ORDER BY quality_score DESC, usage_count DESC
            LIMIT 30
        ''')
        
        candidates = []
        for row in cursor.fetchall():
            cached_embedding = pickle.loads(row[2])
            similarity = cosine_similarity([prompt_embedding], [cached_embedding])[0][0]
            
            if similarity >= self.similarity_threshold:
                candidates.append((similarity, row))
        
        conn.close()
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:limit]
    
    def cache_rag_result(self, query: str, results: List[Dict], response_time: float = 0.0):
        """Cache RAG search results with learning metadata."""
        query_hash = self._hash_query(query)
        query_embedding = self._get_embedding(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute('SELECT usage_count, avg_response_time FROM rag_cache WHERE query_hash = ?', (query_hash,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry with learning
            new_usage = existing[0] + 1
            new_avg_time = (existing[1] * existing[0] + response_time) / new_usage
            
            cursor.execute('''
                UPDATE rag_cache 
                SET usage_count = ?, avg_response_time = ?, last_used = CURRENT_TIMESTAMP
                WHERE query_hash = ?
            ''', (new_usage, new_avg_time, query_hash))
        else:
            # Insert new entry
            cursor.execute('''
                INSERT INTO rag_cache 
                (query_hash, query_text, query_embedding, results, avg_response_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (query_hash, query, pickle.dumps(query_embedding), 
                 pickle.dumps(results), response_time))
        
        conn.commit()
        conn.close()
    
    def get_rag_result(self, query: str) -> Optional[Tuple[List[Dict], Dict]]:
        """Get RAG results from cache with semantic similarity matching."""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        query_hash = self._hash_query(query)
        query_embedding = self._get_embedding(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First try exact match
        cursor.execute('''
            SELECT results, usage_count, success_rate FROM rag_cache 
            WHERE query_hash = ?
        ''', (query_hash,))
        exact_match = cursor.fetchone()
        
        if exact_match:
            results = pickle.loads(exact_match[0])
            metadata = {
                "cache_hit": "exact",
                "usage_count": exact_match[1],
                "success_rate": exact_match[2],
                "response_time": time.time() - start_time
            }
            
            # Update usage
            cursor.execute('''
                UPDATE rag_cache 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE query_hash = ?
            ''', (query_hash,))
            conn.commit()
            conn.close()
            
            self.stats["hits"] += 1
            self._save_stats()
            return results, metadata
        
        # Try semantic similarity matching
        similar_queries = self._find_similar_rag_queries(query, query_embedding)
        
        if similar_queries:
            # Use the best match
            similarity, best_match = similar_queries[0]
            results = pickle.loads(best_match[3])
            
            metadata = {
                "cache_hit": "semantic",
                "similarity": similarity,
                "original_query": best_match[1],
                "usage_count": best_match[4],
                "success_rate": best_match[5],
                "response_time": time.time() - start_time
            }
            
            # Update usage for the matched query
            cursor.execute('''
                UPDATE rag_cache 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE query_hash = ?
            ''', (best_match[0],))
            conn.commit()
            conn.close()
            
            self.stats["hits"] += 1
            self._save_stats()
            return results, metadata
        
        conn.close()
        self.stats["misses"] += 1
        self._save_stats()
        return None
    
    def cache_code_result(self, prompt: str, context: str, temperature: float, 
                         generated_code: str, quality_score: float = 0.0):
        """Cache generated code with quality tracking."""
        prompt_hash = self._hash_prompt(prompt, context, temperature)
        context_hash = self._hash_query(context) if context else ""
        prompt_embedding = self._get_embedding(prompt)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT usage_count FROM code_cache WHERE prompt_hash = ?', (prompt_hash,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE code_cache 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP,
                    quality_score = MAX(quality_score, ?)
                WHERE prompt_hash = ?
            ''', (quality_score, prompt_hash))
        else:
            cursor.execute('''
                INSERT INTO code_cache 
                (prompt_hash, prompt_text, prompt_embedding, context_hash, 
                 generated_code, temperature, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (prompt_hash, prompt, pickle.dumps(prompt_embedding), 
                 context_hash, generated_code, temperature, quality_score))
        
        conn.commit()
        conn.close()
    
    def get_code_result(self, prompt: str, context: str = "", temperature: float = 0.7) -> Optional[Tuple[str, Dict]]:
        """Get cached code result with semantic similarity matching."""
        start_time = time.time()
        
        prompt_hash = self._hash_prompt(prompt, context, temperature)
        prompt_embedding = self._get_embedding(prompt)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try exact match first
        cursor.execute('''
            SELECT generated_code, quality_score, usage_count FROM code_cache 
            WHERE prompt_hash = ?
        ''', (prompt_hash,))
        exact_match = cursor.fetchone()
        
        if exact_match:
            metadata = {
                "cache_hit": "exact",
                "quality_score": exact_match[1],
                "usage_count": exact_match[2],
                "response_time": time.time() - start_time
            }
            
            cursor.execute('''
                UPDATE code_cache 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE prompt_hash = ?
            ''', (prompt_hash,))
            conn.commit()
            conn.close()
            
            return exact_match[0], metadata
        
        # Try semantic similarity
        similar_prompts = self._find_similar_code_prompts(prompt, prompt_embedding)
        
        if similar_prompts:
            similarity, best_match = similar_prompts[0]
            metadata = {
                "cache_hit": "semantic",
                "similarity": similarity,
                "original_prompt": best_match[1],
                "quality_score": best_match[4],
                "usage_count": best_match[5],
                "response_time": time.time() - start_time
            }
            
            cursor.execute('''
                UPDATE code_cache 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE prompt_hash = ?
            ''', (best_match[0],))
            conn.commit()
            conn.close()
            
            return best_match[3], metadata
        
        conn.close()
        return None
    
    def add_user_feedback(self, prompt: str, context: str, temperature: float, 
                         feedback_score: float):
        """Add user feedback to improve cache quality scoring."""
        prompt_hash = self._hash_prompt(prompt, context, temperature)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE code_cache 
            SET user_feedback = (user_feedback + ?) / 2
            WHERE prompt_hash = ?
        ''', (feedback_score, prompt_hash))
        
        conn.commit()
        conn.close()
        
        self.stats["learning_improvements"] += 1
        self._save_stats()
    
    def get_cache_stats(self) -> Dict:
        """Get comprehensive cache statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # RAG cache stats
        cursor.execute('SELECT COUNT(*), AVG(usage_count), AVG(success_rate) FROM rag_cache')
        rag_stats = cursor.fetchone()
        
        # Code cache stats
        cursor.execute('SELECT COUNT(*), AVG(usage_count), AVG(quality_score) FROM code_cache')
        code_stats = cursor.fetchone()
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM rag_cache 
            WHERE last_used > datetime('now', '-24 hours')
        ''')
        recent_rag = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM code_cache 
            WHERE last_used > datetime('now', '-24 hours')
        ''')
        recent_code = cursor.fetchone()[0]
        
        conn.close()
        
        hit_rate = self.stats["hits"] / max(self.stats["total_requests"], 1)
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "rag_cache_size": rag_stats[0] or 0,
            "rag_avg_usage": rag_stats[1] or 0,
            "rag_avg_success": rag_stats[2] or 0,
            "code_cache_size": code_stats[0] or 0,
            "code_avg_usage": code_stats[1] or 0,
            "code_avg_quality": code_stats[2] or 0,
            "recent_rag_activity": recent_rag,
            "recent_code_activity": recent_code
        }
    
    def warm_cache(self, common_queries: List[str] = None):
        """Pre-warm cache with common queries and patterns."""
        if not common_queries:
            common_queries = [
                "create a rotating cube",
                "sphere with lighting",
                "particle system animation",
                "vector field visualization",
                "3D graph plotting",
                "physics simulation",
                "camera controls orbit",
                "texture mapping example"
            ]
        
        print("Warming up cache with common patterns...")
        for query in common_queries:
            # This would typically trigger actual RAG searches
            # but for now we just prepare the embeddings
            self._get_embedding(query)
        
        print(f"Cache warmed with {len(common_queries)} patterns")
    
    def cleanup_old_entries(self, days: int = 30):
        """Clean up old, unused cache entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Remove old RAG entries with low usage
        cursor.execute('''
            DELETE FROM rag_cache 
            WHERE last_used < ? AND usage_count < 2
        ''', (cutoff_date,))
        
        # Remove old code entries with low quality
        cursor.execute('''
            DELETE FROM code_cache 
            WHERE last_used < ? AND quality_score < 0.3 AND usage_count < 2
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()
        
        print(f"Cleaned up cache entries older than {days} days")