"""
Unit tests for Gemini embedding models research and evaluation.

Tests the available free embedding models from the Gemini API
to determine the best option for our project.
"""

import pytest
import asyncio
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

# Import embedding models
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


class TestGeminiEmbeddingModels:
    """Test and evaluate available Gemini embedding models."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Get API key from Streamlit secrets
        try:
            self.api_key = st.secrets.get("GEMINI_API_KEY")
            if not self.api_key or self.api_key == "your-gemini-api-key-here":
                pytest.skip("No valid Gemini API key available")
        except Exception as e:
            pytest.skip(f"Failed to load API key: {e}")
        
        # Test texts for embedding evaluation
        self.test_texts = [
            "Python web application development with FastAPI",
            "Database design and optimization for PostgreSQL",
            "Machine learning model training and evaluation",
            "API integration and testing with RESTful services",
            "Frontend development with React and TypeScript",
            "DevOps and containerization with Docker",
            "Security analysis and vulnerability assessment",
            "Code review and quality assurance processes"
        ]
        
        # Test queries for similarity search
        self.test_queries = [
            "web development",
            "database optimization", 
            "machine learning",
            "API testing",
            "frontend frameworks",
            "containerization",
            "security vulnerabilities",
            "code quality"
        ]
        
        # Available Gemini embedding models to test
        self.embedding_models = [
            "models/embedding-001",  # Current model used in memory_manager.py
            "embedding-001",         # Alternative format
            "models/text-embedding-001",  # Alternative naming
            "text-embedding-001"     # Alternative format
        ]
        
        # Results storage
        self.results = {}
    
    def teardown_method(self):
        """Clean up test artifacts."""
        # Clean up any temporary vector stores
        temp_dirs = Path(".").glob("chroma_db_*")
        for temp_dir in temp_dirs:
            if temp_dir.is_dir():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_available_embedding_models(self):
        """Test which embedding models are available and working."""
        print("\n🔍 Testing Available Gemini Embedding Models...")
        
        working_models = []
        
        for model_name in self.embedding_models:
            try:
                print(f"\n📋 Testing model: {model_name}")
                
                # Create embeddings instance
                embeddings = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    google_api_key=self.api_key
                )
                
                # Test basic embedding generation
                test_text = "Hello, world!"
                embedding = await embeddings.aembed_query(test_text)
                
                # Validate embedding
                assert isinstance(embedding, list), f"Embedding should be a list, got {type(embedding)}"
                assert len(embedding) > 0, f"Embedding should not be empty"
                assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding should contain numbers"
                
                print(f"✅ {model_name}: SUCCESS - Embedding dimension: {len(embedding)}")
                working_models.append({
                    "model": model_name,
                    "dimension": len(embedding),
                    "status": "working"
                })
                
            except Exception as e:
                print(f"❌ {model_name}: FAILED - {str(e)}")
                working_models.append({
                    "model": model_name,
                    "dimension": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Store results
        self.results["available_models"] = working_models
        
        # Assert that at least one model works
        working_count = sum(1 for model in working_models if model["status"] == "working")
        assert working_count > 0, "No working embedding models found"
        
        print(f"\n📊 Summary: {working_count}/{len(self.embedding_models)} models working")
        return working_models
    
    @pytest.mark.asyncio
    async def test_embedding_quality_and_performance(self):
        """Test embedding quality and performance for working models."""
        print("\n⚡ Testing Embedding Quality and Performance...")
        
        # Get working models from previous test
        working_models = [m for m in self.results.get("available_models", []) 
                         if m["status"] == "working"]
        
        if not working_models:
            pytest.skip("No working models to test")
        
        quality_results = []
        
        for model_info in working_models:
            model_name = model_info["model"]
            print(f"\n🔬 Testing quality for: {model_name}")
            
            try:
                # Create embeddings instance
                embeddings = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    google_api_key=self.api_key
                )
                
                # Test performance
                start_time = time.time()
                embeddings_list = await embeddings.aembed_documents(self.test_texts)
                end_time = time.time()
                
                performance_time = end_time - start_time
                avg_time_per_text = performance_time / len(self.test_texts)
                
                # Test embedding consistency
                embedding_dimensions = [len(emb) for emb in embeddings_list]
                dimension_consistency = len(set(embedding_dimensions)) == 1
                
                # Test semantic similarity (basic test)
                query_embedding = await embeddings.aembed_query("software development")
                similarities = []
                
                for doc_embedding in embeddings_list:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append(similarity)
                
                # Quality metrics
                avg_similarity = np.mean(similarities)
                similarity_variance = np.var(similarities)
                
                quality_result = {
                    "model": model_name,
                    "performance": {
                        "total_time": performance_time,
                        "avg_time_per_text": avg_time_per_text,
                        "texts_per_second": len(self.test_texts) / performance_time
                    },
                    "quality": {
                        "dimension_consistency": dimension_consistency,
                        "avg_similarity": avg_similarity,
                        "similarity_variance": similarity_variance,
                        "embedding_dimension": len(embeddings_list[0])
                    }
                }
                
                print(f"✅ {model_name}:")
                print(f"   Performance: {quality_result['performance']['texts_per_second']:.2f} texts/sec")
                print(f"   Dimension: {quality_result['quality']['embedding_dimension']}")
                print(f"   Avg Similarity: {quality_result['quality']['avg_similarity']:.4f}")
                
                quality_results.append(quality_result)
                
            except Exception as e:
                print(f"❌ {model_name}: Quality test failed - {str(e)}")
                quality_results.append({
                    "model": model_name,
                    "error": str(e)
                })
        
        self.results["quality_results"] = quality_results
        return quality_results
    
    @pytest.mark.asyncio
    async def test_vector_store_integration(self):
        """Test integration with Chroma vector store."""
        print("\n🗄️ Testing Vector Store Integration...")
        
        # Get best performing model
        quality_results = self.results.get("quality_results", [])
        working_results = [r for r in quality_results if "error" not in r]
        
        if not working_results:
            pytest.skip("No working models for vector store test")
        
        # Sort by performance (texts per second)
        best_model = max(working_results, 
                        key=lambda x: x["performance"]["texts_per_second"])
        
        print(f"🎯 Using best model: {best_model['model']}")
        
        try:
            # Create embeddings
            embeddings = GoogleGenerativeAIEmbeddings(
                model=best_model["model"],
                google_api_key=self.api_key
            )
            
            # Create vector store
            persist_directory = f"chroma_db_test_{int(time.time())}"
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            
            # Create documents
            documents = [
                Document(
                    page_content=text,
                    metadata={"source": f"test_{i}", "category": "development"}
                )
                for i, text in enumerate(self.test_texts)
            ]
            
            # Add documents to vector store
            start_time = time.time()
            vector_store.add_documents(documents)
            add_time = time.time() - start_time
            
            # Test similarity search
            search_results = []
            for query in self.test_queries:
                start_time = time.time()
                results = vector_store.similarity_search_with_relevance_scores(
                    query, k=3
                )
                search_time = time.time() - start_time
                
                search_results.append({
                    "query": query,
                    "results": len(results),
                    "search_time": search_time,
                    "top_result": results[0][0].page_content if results else None,
                    "top_score": results[0][1] if results else None
                })
            
            # Calculate metrics
            avg_search_time = np.mean([r["search_time"] for r in search_results])
            avg_top_score = np.mean([r["top_score"] for r in search_results if r["top_score"] is not None])
            
            integration_result = {
                "model": best_model["model"],
                "vector_store": "Chroma",
                "performance": {
                    "add_documents_time": add_time,
                    "avg_search_time": avg_search_time,
                    "documents_added": len(documents)
                },
                "quality": {
                    "avg_top_score": avg_top_score,
                    "successful_searches": len([r for r in search_results if r["top_score"] is not None])
                }
            }
            
            print(f"✅ Vector store integration successful:")
            print(f"   Documents added: {integration_result['performance']['documents_added']}")
            print(f"   Add time: {integration_result['performance']['add_documents_time']:.3f}s")
            print(f"   Avg search time: {integration_result['performance']['avg_search_time']:.3f}s")
            print(f"   Avg top score: {integration_result['quality']['avg_top_score']:.4f}")
            
            self.results["integration_result"] = integration_result
            return integration_result
            
        except Exception as e:
            print(f"❌ Vector store integration failed: {str(e)}")
            self.results["integration_result"] = {"error": str(e)}
            return {"error": str(e)}
    
    @pytest.mark.asyncio
    async def test_cost_analysis(self):
        """Analyze cost implications of different models."""
        print("\n💰 Cost Analysis...")
        
        # Note: Gemini embedding models are currently free
        # This test documents the cost structure for future reference
        
        cost_info = {
            "models/embedding-001": {
                "cost_per_1k_tokens": 0.0,  # Free
                "max_tokens_per_request": 2048,
                "rate_limit": "Not specified",
                "availability": "Free tier"
            },
            "embedding-001": {
                "cost_per_1k_tokens": 0.0,  # Free
                "max_tokens_per_request": 2048,
                "rate_limit": "Not specified", 
                "availability": "Free tier"
            }
        }
        
        print("✅ All Gemini embedding models are currently FREE")
        print("💰 Cost per 1K tokens: $0.00")
        print("🚀 No rate limits specified for free tier")
        
        self.results["cost_analysis"] = cost_info
        return cost_info
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @pytest.mark.asyncio
    async def test_recommendation_analysis(self):
        """Analyze results and provide recommendations."""
        print("\n📋 Recommendation Analysis...")
        
        # Compile all results
        available_models = self.results.get("available_models", [])
        quality_results = self.results.get("quality_results", [])
        integration_result = self.results.get("integration_result", {})
        cost_analysis = self.results.get("cost_analysis", {})
        
        # Find best model based on multiple criteria
        working_models = [m for m in available_models if m["status"] == "working"]
        
        if not working_models:
            print("❌ No working models found")
            return
        
        # Score models based on performance and quality
        model_scores = []
        
        for model_info in working_models:
            model_name = model_info["model"]
            
            # Find quality results for this model
            quality_result = next((q for q in quality_results if q.get("model") == model_name), None)
            
            if quality_result and "error" not in quality_result:
                # Calculate composite score
                performance_score = quality_result["performance"]["texts_per_second"]
                quality_score = quality_result["quality"]["avg_similarity"]
                consistency_score = 1.0 if quality_result["quality"]["dimension_consistency"] else 0.0
                
                # Normalize scores (assuming reasonable ranges)
                normalized_performance = min(performance_score / 10.0, 1.0)  # Cap at 10 texts/sec
                normalized_quality = max(0, min(quality_score, 1.0))
                
                composite_score = (normalized_performance * 0.4 + 
                                 normalized_quality * 0.4 + 
                                 consistency_score * 0.2)
                
                model_scores.append({
                    "model": model_name,
                    "composite_score": composite_score,
                    "performance_score": normalized_performance,
                    "quality_score": normalized_quality,
                    "consistency_score": consistency_score,
                    "dimension": quality_result["quality"]["embedding_dimension"]
                })
        
        # Sort by composite score
        model_scores.sort(key=lambda x: x["composite_score"], reverse=True)
        
        # Generate recommendations
        recommendations = {
            "best_model": model_scores[0] if model_scores else None,
            "all_models_ranked": model_scores,
            "cost_effective": True,  # All models are free
            "recommendation": "Use the highest scoring model for best performance"
        }
        
        print("\n🏆 Model Rankings:")
        for i, score in enumerate(model_scores):
            print(f"{i+1}. {score['model']}: {score['composite_score']:.3f}")
            print(f"   Performance: {score['performance_score']:.3f}, Quality: {score['quality_score']:.3f}")
        
        if model_scores:
            best = model_scores[0]
            print(f"\n🎯 RECOMMENDATION: Use {best['model']}")
            print(f"   Composite Score: {best['composite_score']:.3f}")
            print(f"   Embedding Dimension: {best['dimension']}")
            print(f"   Cost: FREE")
        
        self.results["recommendations"] = recommendations
        return recommendations
