#!/usr/bin/env python3
"""
RAG Library Diagnostics
=======================

Diagnose library issues in RAG Management App.
Checks all imports and identifies missing/incompatible libraries.

Usage:
    python scripts/diagnose_rag_libraries.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🔍 RAG LIBRARY DIAGNOSTICS")
print("=" * 70)
print()

issues = []
warnings = []

# Test 1: Streamlit
print("📦 Checking Streamlit...")
try:
    import streamlit as st
    print(f"   ✅ streamlit {st.__version__}")
except ImportError as e:
    print(f"   ❌ streamlit MISSING: {e}")
    issues.append("streamlit not installed")

# Test 2: LangChain Core
print("📦 Checking LangChain core...")
try:
    import langchain
    import langchain_core
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print(f"   ✅ langchain {langchain.__version__}")
    print(f"   ✅ langchain-core {langchain_core.__version__}")
except ImportError as e:
    print(f"   ❌ LangChain MISSING: {e}")
    issues.append("langchain or langchain-core not installed")

# Test 3: Qdrant Client
print("📦 Checking Qdrant...")
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    print("   ✅ qdrant-client installed")
except ImportError as e:
    print(f"   ❌ qdrant-client MISSING: {e}")
    issues.append("qdrant-client not installed")

# Test 4: Qdrant LangChain Integration (NEW API)
print("📦 Checking langchain-qdrant (NEW API)...")
try:
    from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
    print("   ✅ langchain-qdrant (NEW API) installed")
    print("   ✅ Using QdrantVectorStore with hybrid search support")
except ImportError as e:
    print(f"   ⚠️  langchain-qdrant (NEW API) not available: {e}")
    warnings.append("Using old Qdrant API")
    
    # Fallback to old API
    try:
        from langchain_qdrant import Qdrant
        print("   ✅ langchain-qdrant (OLD API) available as fallback")
    except ImportError as e2:
        print(f"   ❌ langchain-qdrant MISSING: {e2}")
        issues.append("langchain-qdrant not installed")

# Test 5: Embeddings (HuggingFace - free local)
print("📦 Checking HuggingFace embeddings...")
try:
    from langchain_huggingface.embeddings import HuggingFaceEmbeddings
    print("   ✅ langchain-huggingface (primary) installed")
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("   ✅ HuggingFaceEmbeddings (community fallback) available")
    except ImportError as e:
        print(f"   ❌ HuggingFace embeddings MISSING: {e}")
        issues.append("langchain-huggingface not installed")

# Test 6: OpenAI Embeddings (optional)
print("📦 Checking OpenAI embeddings (optional)...")
try:
    from langchain_openai import OpenAIEmbeddings
    print("   ✅ langchain-openai available (optional)")
except ImportError:
    print("   ⚠️  langchain-openai not available (optional - OK)")

# Test 7: Sentence Transformers
print("📦 Checking sentence-transformers...")
try:
    import sentence_transformers
    print(f"   ✅ sentence-transformers installed")
except ImportError as e:
    print(f"   ❌ sentence-transformers MISSING: {e}")
    issues.append("sentence-transformers not installed")

# Test 8: Torch (required for embeddings)
print("📦 Checking PyTorch...")
try:
    import torch
    print(f"   ✅ torch {torch.__version__}")
except ImportError as e:
    print(f"   ❌ torch MISSING: {e}")
    issues.append("torch not installed")

# Test 9: Document Loaders
print("📦 Checking document loaders...")
try:
    from utils.rag.document_loader import DocumentLoader
    print("   ✅ DocumentLoader available")
except ImportError as e:
    print(f"   ⚠️  DocumentLoader import issue: {e}")
    warnings.append("DocumentLoader may have issues")

# Test 10: ContextEngine
print("📦 Checking ContextEngine...")
try:
    from context.context_engine import ContextEngine
    from models.config import ContextConfig
    print("   ✅ ContextEngine available")
except ImportError as e:
    print(f"   ❌ ContextEngine MISSING: {e}")
    issues.append("ContextEngine import failed")

# Test 11: NumPy version (important for compatibility)
print("📦 Checking NumPy version...")
try:
    import numpy as np
    numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
    print(f"   ✅ numpy {np.__version__}")
    if numpy_version >= (2, 0):
        print("   ✅ NumPy 2.0+ (compatible with modern libraries)")
    else:
        print("   ⚠️  NumPy 1.x (may have compatibility issues)")
        warnings.append("Consider upgrading to NumPy 2.0+")
except ImportError as e:
    print(f"   ❌ numpy MISSING: {e}")
    issues.append("numpy not installed")

print()
print("=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)

if not issues and not warnings:
    print("✅ ALL LIBRARIES OK - RAG app should work!")
    print()
    print("🚀 Next step: Run the app")
    print("   streamlit run apps/rag_management_app.py")
    sys.exit(0)

if warnings:
    print()
    print("⚠️  WARNINGS:")
    for w in warnings:
        print(f"   - {w}")

if issues:
    print()
    print("❌ CRITICAL ISSUES:")
    for i in issues:
        print(f"   - {i}")
    print()
    print("🔧 FIXING INSTRUCTIONS:")
    print()
    
    if any("streamlit" in i for i in issues):
        print("   Install Streamlit:")
        print("   pip install streamlit==1.28.2")
        print()
    
    if any("langchain" in i for i in issues):
        print("   Install LangChain:")
        print("   pip install langchain==0.3.27 langchain-core>=0.3.78")
        print()
    
    if any("qdrant" in i for i in issues):
        print("   Install Qdrant:")
        print("   pip install qdrant-client>=1.9.0 langchain-qdrant>=0.2.1")
        print()
    
    if any("huggingface" in i.lower() for i in issues):
        print("   Install HuggingFace embeddings:")
        print("   pip install langchain-huggingface==0.3.1")
        print()
    
    if any("torch" in i for i in issues):
        print("   Install PyTorch:")
        print("   pip install torch>=2.5.1")
        print()
    
    if any("sentence" in i for i in issues):
        print("   Install sentence-transformers:")
        print("   pip install sentence-transformers>=3.4.1")
        print()
    
    print("   OR install all RAG dependencies:")
    print("   pip install -r requirements.txt")
    print()
    
    sys.exit(1)
else:
    print()
    print("✅ No critical issues, but check warnings above")
    sys.exit(0)

