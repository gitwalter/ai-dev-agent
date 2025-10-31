# US-RAG-008: Synthetic Data & RAG Flywheel

**Epic**: RAG System Enhancement  
**Story ID**: US-RAG-008  
**Priority**: Medium (after Phase 0-3 complete)  
**Story Points**: 8  
**Sprint**: Future (Sprint 8+)  
**Status**: 📋 Backlog  

---

## User Story

**As a** RAG system operator  
**I want** synthetic data generation and continuous improvement flywheel  
**So that** I can systematically improve RAG quality before and after launch

---

## Business Value

**Problem**: Current RAG development is:
- Reactive (wait for user complaints)
- No baseline metrics before launch
- Hard to identify what to improve
- Can't test without real users

**Solution**: Implement RAG Flywheel pattern:
1. Generate synthetic questions per chunk
2. Test retrieval with fast evals (precision/recall)
3. Iterate rapidly (milliseconds per test)
4. Cluster real questions by topic
5. Continuously improve based on data

**Value**: 
- Launch with confidence (baseline metrics)
- Detect issues early (before users complain)
- Focus improvements (leading metrics)
- Adapt to changing needs (concept drift detection)

**Reference**: [The RAG Playbook](https://jxnl.co/writing/2024/08/19/rag-flywheel/) by Jason Liu

---

## Acceptance Criteria

### Phase 1: Synthetic Data Generation

**AC-1.1**: Generate synthetic questions for each document chunk
- [ ] Implement `SyntheticQuestionGenerator` using LLM
- [ ] Generate 3-5 questions per chunk
- [ ] Store questions with chunk metadata
- [ ] Cover different question types (factual, conceptual, procedural)

**AC-1.2**: Create baseline retrieval evaluation
- [ ] Implement precision/recall calculator
- [ ] Run on all synthetic questions
- [ ] Establish baseline scores per topic
- [ ] Fast execution (<1 sec per question)

### Phase 2: Fast Evaluation System

**AC-2.1**: Unit test-like retrieval tests
- [ ] Test: query → retrieve → check if correct chunk in results
- [ ] Blazing fast (milliseconds per test)
- [ ] Run on every code change
- [ ] Track precision/recall trends

**AC-2.2**: Leading metrics dashboard
- [ ] Experiments run per week
- [ ] Precision/recall improvements
- [ ] Eval suite execution time
- [ ] NOT overall quality (lagging metric)

### Phase 3: Real-World Data Clustering

**AC-3.1**: Question clustering system
- [ ] Unsupervised learning to identify topics
- [ ] Domain expert labeling
- [ ] Few-shot classifier for new questions
- [ ] Monitor "Other" category growth (concept drift)

**AC-3.2**: Per-cluster analytics
- [ ] Question frequency by topic
- [ ] Cosine similarity scores within clusters
- [ ] User satisfaction per topic
- [ ] Identify gaps and opportunities

### Phase 4: Continuous Improvement Loop

**AC-4.1**: Production monitoring
- [ ] Classify all production questions by topic
- [ ] Track distribution changes over time
- [ ] Alert on significant pattern shifts
- [ ] Real-time dashboard

**AC-4.2**: Systematic experimentation
- [ ] Prioritize improvements by business impact
- [ ] A/B test changes (not just local evals)
- [ ] Measure actual user satisfaction
- [ ] Iterate based on results

---

## Technical Implementation

### Synthetic Question Generation

```python
class SyntheticQuestionGenerator:
    """Generate synthetic questions for RAG evaluation."""
    
    def generate_questions(self, chunk: str, num_questions: int = 3) -> List[str]:
        """Generate diverse questions for a document chunk."""
        prompt = f"""Generate {num_questions} diverse questions that can be answered 
        using the following text chunk:
        
        {chunk}
        
        Question types:
        1. Factual (What is X?)
        2. Conceptual (How does X work?)
        3. Procedural (How to do X?)
        
        Return only the questions, one per line."""
        
        response = self.llm.invoke(prompt)
        questions = response.content.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
```

### Fast Evaluation

```python
class FastRetrievalEvaluator:
    """Lightning-fast retrieval evaluation using synthetic data."""
    
    def evaluate_retrieval(self, questions: List[SyntheticQuestion]) -> Metrics:
        """Run fast retrieval evaluation."""
        correct = 0
        total = len(questions)
        
        for q in questions:
            # Fast retrieval test
            results = self.retriever.search(q.question, k=5)
            if q.source_chunk_id in [r.chunk_id for r in results]:
                correct += 1
        
        return Metrics(
            precision=correct / total,
            recall=correct / total,  # Simplified for single-answer questions
            eval_time_ms=(time.time() - start) * 1000
        )
```

### Question Clustering

```python
class QuestionClusterer:
    """Cluster questions by topic for targeted improvements."""
    
    def cluster_questions(self, questions: List[str]) -> ClusterResult:
        """Unsupervised clustering of user questions."""
        # 1. Embed questions
        embeddings = self.embed_model.embed(questions)
        
        # 2. Cluster
        clusters = KMeans(n_clusters=8).fit(embeddings)
        
        # 3. Label with domain expert or LLM
        cluster_labels = self._label_clusters(clusters)
        
        # 4. Create few-shot classifier
        classifier = self._train_classifier(questions, clusters, cluster_labels)
        
        return ClusterResult(clusters, cluster_labels, classifier)
    
    def monitor_concept_drift(self, new_questions: List[str]) -> Alert:
        """Monitor for concept drift via 'Other' category growth."""
        classifications = self.classifier.classify(new_questions)
        
        other_percentage = sum(1 for c in classifications if c == 'Other') / len(classifications)
        
        if other_percentage > self.drift_threshold:
            return Alert(
                type='concept_drift',
                message=f"'Other' category at {other_percentage:.1%} (threshold: {self.drift_threshold:.1%})",
                action='Review new question patterns and update clusters'
            )
```

---

## Success Metrics

### Leading Metrics (Primary Focus)
- **Experiments per week**: Target 10+ retrieval experiments
- **Precision improvement**: Target +5% per sprint
- **Eval suite speed**: Target <10 sec for full suite
- **Concept drift detection**: Alert within 1 week

### Lagging Metrics (Track, Don't Obsess)
- Overall user satisfaction
- Answer quality scores
- System uptime

---

## Dependencies

- **Requires**: US-RAG-006 Phase 0-2 complete (working RAG)
- **Nice to have**: US-RAG-006 Phase 3 (HITL) for better feedback loop
- **Tools needed**: scikit-learn for clustering, embeddings model

---

## Open Questions

1. How many synthetic questions per chunk? (Suggest: 3-5)
2. Which clustering algorithm? (Suggest: KMeans or HDBSCAN)
3. Drift threshold for "Other" category? (Suggest: 15%)
4. How often to regenerate synthetic data? (Suggest: weekly)

---

## Notes

- Synthetic data enables testing before launch
- Leading metrics > lagging metrics for actionable insights
- Real questions are always stranger than synthetic (expect surprises)
- "Other" category growth = your canary in the coal mine
- This is a continuous process, not a one-time setup

**Reference Articles**:
- [The RAG Playbook](https://jxnl.co/writing/2024/08/19/rag-flywheel/)
- [How to build a terrible RAG system](https://jxnl.co/writing/2024/01/07/inverted-thinking-rag/)

---

**Created**: 2025-01-29  
**Related**: US-RAG-006 (foundation), US-RAG-009 (reports)

