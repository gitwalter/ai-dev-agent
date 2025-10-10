# US-RAG-002: RAG Document Database Integration

**Epic**: EPIC-0 - Development Excellence
**Sprint**: Backlog (Future Implementation)  
**Priority**: 🟡 MEDIUM  
**Story Points**: 8  
**Assignee**: RAG System Team  
**Status**: 📋 BACKLOG

## 📋 **User Story**

**As a** RAG system user and developer  
**I want** RAG documents stored in a structured SQLite database instead of file-based storage  
**So that** I have better query performance, rich metadata management, data integrity, and preparation for vector database integration

## 🎯 **Problem Statement**

Currently, the RAG document system uses file-based storage with a separate JSON metadata file. This approach has several limitations:

### **Current Limitations**
- **Query Performance**: File system scanning is slower than database queries
- **Metadata Management**: JSON file becomes unwieldy with many documents
- **Data Integrity**: No transactional guarantees for document operations
- **Search Capabilities**: Limited to simple text searches, no advanced filtering
- **Scalability**: Performance degrades with large number of documents
- **Relationship Tracking**: Difficult to track document relationships and dependencies

### **Future Needs**
- **Vector Database Integration**: Need structured storage for future FAISS/Qdrant integration
- **Advanced Queries**: Filter by multiple metadata fields, date ranges, tags
- **Analytics**: Track document usage, access patterns, effectiveness
- **Versioning**: Support document version history and rollback
- **Access Control**: User-based access permissions for documents

## 💡 **Solution Overview**

Migrate RAG document storage from file-based to SQLite database while maintaining backward compatibility and preparing for future vector database integration.

### **Database Schema**
```sql
CREATE TABLE rag_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    file_path TEXT,
    agent_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);

CREATE TABLE rag_document_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES rag_documents(id) ON DELETE CASCADE
);

CREATE TABLE rag_document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY (document_id) REFERENCES rag_documents(id) ON DELETE CASCADE
);

CREATE TABLE rag_document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_metadata TEXT,
    FOREIGN KEY (document_id) REFERENCES rag_documents(id) ON DELETE CASCADE
);

CREATE TABLE rag_document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT,
    FOREIGN KEY (document_id) REFERENCES rag_documents(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_rag_docs_doc_id ON rag_documents(doc_id);
CREATE INDEX idx_rag_docs_agent ON rag_documents(agent_name);
CREATE INDEX idx_rag_docs_source_type ON rag_documents(source_type);
CREATE INDEX idx_rag_docs_status ON rag_documents(status);
CREATE INDEX idx_rag_tags_doc ON rag_document_tags(document_id);
CREATE INDEX idx_rag_tags_tag ON rag_document_tags(tag);
CREATE INDEX idx_rag_chunks_doc ON rag_document_chunks(document_id);
```

### **Migration Strategy**
1. **Phase 1**: Create new database schema alongside existing file storage
2. **Phase 2**: Implement dual-write (write to both file and database)
3. **Phase 3**: Migrate existing documents to database
4. **Phase 4**: Switch to database-only reads
5. **Phase 5**: Remove file-based storage (optional, keep as backup)

## ✅ **Acceptance Criteria**

### **AC-1: Database Schema and Setup**
- [ ] SQLite database created with proper schema
- [ ] All tables, indexes, and foreign keys implemented
- [ ] Database migrations system implemented
- [ ] Database connection pooling configured
- [ ] Backup and recovery procedures documented

### **AC-2: Document CRUD Operations**
- [ ] Create documents in database with full metadata
- [ ] Read documents with efficient queries
- [ ] Update documents with version tracking
- [ ] Delete documents with cascade handling
- [ ] Batch operations for multiple documents

### **AC-3: Advanced Query Capabilities**
- [ ] Filter by multiple metadata fields
- [ ] Full-text search on content
- [ ] Filter by tags (AND/OR operations)
- [ ] Filter by date ranges (created, updated)
- [ ] Filter by agent association
- [ ] Pagination for large result sets

### **AC-4: Backward Compatibility**
- [ ] Existing file-based documents automatically migrated
- [ ] API compatibility maintained (no breaking changes)
- [ ] Fallback to file-based storage if database unavailable
- [ ] Data validation to ensure consistency
- [ ] Rollback capability if migration fails

### **AC-5: Version Control and History**
- [ ] Document version history tracking
- [ ] View previous versions of documents
- [ ] Restore documents to previous versions
- [ ] Track who made changes and when
- [ ] Change reason documentation

### **AC-6: Performance and Scalability**
- [ ] Query performance < 50ms for single document
- [ ] Bulk operations < 500ms for 100 documents
- [ ] Database size optimization (vacuum, compression)
- [ ] Efficient indexing strategy
- [ ] Memory usage optimization

### **AC-7: Vector Database Preparation**
- [ ] Schema supports future embedding storage
- [ ] Chunk management for vector indexing
- [ ] Metadata structure compatible with FAISS/Qdrant
- [ ] Document-chunk relationship tracking
- [ ] Embedding update tracking

## 🔧 **Technical Implementation**

### **Database Manager Class**
```python
class RAGDatabaseManager:
    """Manage RAG documents in SQLite database."""
    
    def __init__(self, db_path: str = "data/rag_documents/rag_documents.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema."""
        # Create tables if not exist
        # Apply migrations
        pass
    
    def add_document(self, doc: RAGDocument) -> int:
        """Add a document to the database."""
        # Insert document with metadata, tags, chunks
        pass
    
    def get_document(self, doc_id: str) -> Optional[RAGDocument]:
        """Get document by ID."""
        pass
    
    def search_documents(self, query: RAGDocumentQuery) -> List[RAGDocument]:
        """Search documents with advanced filtering."""
        pass
    
    def update_document(self, doc_id: str, updates: Dict) -> bool:
        """Update document and create version."""
        pass
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and related data."""
        pass
```

### **Migration Tool**
```python
class RAGStorageMigration:
    """Migrate from file-based to database storage."""
    
    def migrate_all_documents(self):
        """Migrate all existing file-based documents to database."""
        # Read all files
        # Parse metadata
        # Insert into database
        # Validate migration
        pass
    
    def validate_migration(self) -> MigrationReport:
        """Validate that all documents migrated successfully."""
        pass
    
    def rollback_migration(self):
        """Rollback migration if needed."""
        pass
```

## 📊 **Success Metrics**

### **Performance Metrics**
- **Query Speed**: < 50ms for single document retrieval
- **Bulk Operations**: < 500ms for 100 documents
- **Search Performance**: < 200ms for full-text search
- **Database Size**: < 10% increase over file-based storage

### **Functional Metrics**
- **Migration Success**: 100% of existing documents migrated
- **Data Integrity**: 100% match between source and migrated data
- **Query Accuracy**: 100% accuracy in filtered searches
- **Backward Compatibility**: 100% API compatibility maintained

### **Operational Metrics**
- **Uptime**: No downtime during migration
- **Error Rate**: < 0.1% error rate in operations
- **Recovery Time**: < 1 minute for database recovery
- **Backup Success**: 100% successful daily backups

## 🔗 **Dependencies**

### **Technical Dependencies**
- **US-RAG-001**: Current RAG system implementation
- **SQLite3**: Python sqlite3 module
- **Context Engine**: Integration with existing context engine
- **Prompt Editor**: Updated to use database backend

### **Blocked By**
- None (can implement independently)

### **Blocks**
- **Vector Database Integration**: Need structured storage first
- **Advanced RAG Features**: Need query capabilities
- **Analytics Dashboard**: Need usage tracking

## 🚀 **Implementation Plan**

### **Week 1: Database Design and Setup**
- **Day 1-2**: Design and implement database schema
- **Day 3**: Create database manager class
- **Day 4**: Implement CRUD operations
- **Day 5**: Write unit tests for database operations

### **Week 2: Migration and Integration**
- **Day 1-2**: Implement migration tool
- **Day 3**: Test migration with existing documents
- **Day 4**: Update PromptEditor to use database
- **Day 5**: Integration testing and validation

## 🎯 **Definition of Done**

- [ ] Database schema created and documented
- [ ] All CRUD operations implemented and tested
- [ ] Migration tool created and validated
- [ ] Existing documents successfully migrated
- [ ] Backward compatibility maintained
- [ ] Performance metrics met
- [ ] Integration tests passing (95%+ coverage)
- [ ] Documentation complete (user and technical)
- [ ] Code review completed
- [ ] Production deployment ready

## 📝 **Notes**

### **Design Decisions**
- **SQLite Choice**: Simple, embedded, no separate server required
- **Dual-Write Phase**: Ensures safety during transition
- **Version History**: Track all changes for audit and rollback
- **Chunk Storage**: Prepare for vector database integration

### **Future Enhancements**
- **Vector Storage**: Add embedding columns for FAISS/Qdrant
- **Full-Text Search**: Leverage SQLite FTS5 extension
- **Access Control**: Add user permissions table
- **Analytics**: Track document usage and effectiveness

### **Risks and Mitigation**
- **Migration Risk**: Implement rollback and validation
- **Performance Risk**: Use proper indexing and optimization
- **Compatibility Risk**: Maintain dual storage during transition
- **Data Loss Risk**: Implement comprehensive backups

---

**Created**: 2025-01-10  
**Last Updated**: 2025-01-10  
**Story Type**: Technical Enhancement  
**Risk Level**: Medium (data migration always carries risk)  
**Innovation Level**: Incremental (standard database migration)  
**Strategic Impact**: Foundation for advanced RAG capabilities

