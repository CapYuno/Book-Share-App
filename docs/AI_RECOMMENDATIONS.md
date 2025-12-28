# AI Recommendation System Documentation

## Overview

The BookShare recommendation system uses **TF-IDF (Term Frequency-Inverse Document Frequency)** content-based filtering to suggest similar books based on book metadata.

## Algorithm: TF-IDF + Cosine Similarity

### How It Works

1. **Feature Extraction**: For each book, we combine:
   - Title (weighted 2x)
   - Author (weighted 2x)
   - Genre (weighted 3x)
   - Description (1x)

2. **Vectorization**: Text is converted to numerical TF-IDF vectors
   - Min document frequency: 2
   - Max features: 1000
   - N-gram range: 1-2 (unigrams and bigrams)
   - Stop words: English

3. **Similarity Computation**: Cosine similarity between book vectors
   - Ranges from 0 (completely different) to 1 (identical)
   - Higher scores = more similar content

4. **Recommendation Selection**: Top-K books with highest similarity scores

## API Endpoints

### Get Book Recommendations

```http
GET /recommendations/books/<book_id>?top=3
```

**Response:**
```json
{
  "book_id": 123,
  "book_title": "The Great Gatsby",
  "recommendations": [
    {
      "id": 456,
      "title": "This Side of Paradise",
      "author": "F. Scott Fitzgerald",
      "genre": "Fiction",
      "similarity_score": 0.8234
    }
  ],
  "count": 3,
  "latency_ms": 15.43,
  "algorithm": "TF-IDF + Cosine Similarity"
}
```

### Get Borrower Recommendations

Get personalized recommendations based on reading history:

```http
GET /recommendations/borrowers/<borrower_id>?top=3
```

### Rebuild Cache

Rebuild the TF-IDF model (call after bulk book updates):

```http
POST /recommendations/rebuild
```

## CLI Commands

```bash
# Rebuild recommendation cache
flask rebuild-recs
```

## Performance Characteristics

### Time Complexity
- **Model building**: O(n × m) where n = books, m = avg features per book
- **Recommendation query**: O(n) where n = total books
- **Expected latency**: < 100ms for < 5000 books

### Space Complexity
- **TF-IDF matrix**: O(n × v) where n = books, v = vocabulary size
- **Typical size**: ~5MB for 1000 books with 1000 features

## Performance Benchmarks

Based on testing with seeded data:

| Books | Build Time | Query Time | Memory |
|-------|-----------|-----------|---------|
| 100   | ~50ms     | ~5ms      | ~1MB    |
| 1,000 | ~200ms    | ~15ms     | ~5MB    |
| 5,000 | ~1s       | ~50ms     | ~25MB   |

*Note: Times measured on development machine*

## Feature Weighting Strategy

Different book attributes are weighted by repetition in the feature text:

```python
Title:       2x  (repeated twice)
Author:      2x  (repeated twice)
Genre:       3x  (repeated three times)
Description: 1x  (included once)
```

**Rationale**: Genre and author are strong indicators of book similarity. Title matters for series detection.

## Caching Strategy

The TF-IDF model is cached to disk (`tfidf_cache.pkl`) to avoid rebuilding on every request:

1. **On first request**: Build model, cache to disk
2. **Subsequent requests**: Load from cache (fast)
3. **On book updates**: Invalidate and rebuild cache

### When to Rebuild

Rebuild the cache when:
- Books are added/updated/deleted
- Configuration changes (ngram range, max features, etc.)
- Model accuracy needs improvement

## Evaluation Metrics

### Precision@K

Measures how many of the top-K recommendations are relevant:

```
Precision@3 = (Relevant recommendations in top 3) / 3
```

**Target**: ≥ 0.6 (60% of recommendations should be relevant)

### Latency

**Target**: ≤ 2 seconds per query (as per NFRs)

### Coverage

Percentage of books that have at least one recommendation:

```
Coverage = (Books with recommendations) / Total books
```

**Target**: ≥ 0.9 (90% coverage)

## Limitations

1. **Cold Start**: New books without descriptions have poor recommendations
2. **Popularity Bias**: Does not account for book popularity
3. **No Collaborative Filtering**: Doesn't learn from user behavior patterns
4. **Language-Specific**: Optimized for English text

## Future Enhancements

1. **Hybrid Approach**: Combine content-based with collaborative filtering
2. **Deep Learning**: Use BERT embeddings instead of TF-IDF
3. **Metadata Enhancement**: Include publisher, tags, ratings
4. **Real-time Updates**: Incremental model updates instead of full rebuild
5. **A/B Testing**: Compare different algorithms

## Example Usage

### Python (from Flask shell)

```python
from app.services.recommendations import get_recommendation_engine

# Get engine
engine = get_recommendation_engine()

# Get recommendations for book ID 123
recommendations = engine.get_recommendations(123, top_k=5)

for book_id, similarity in recommendations:
    print(f"Book {book_id}: {similarity:.2%} similar")
```

### JavaScript (from frontend)

```javascript
fetch('/recommendations/books/123?top=5')
  .then(res => res.json())
  .then(data => {
    console.log('Recommendations:', data.recommendations);
    console.log('Latency:', data.latency_ms, 'ms');
  });
```

## Testing

Run recommendation tests:

```bash
pytest tests/unit/test_recommendations.py -v
```

### Test Coverage

- ✓ Model building
- ✓ Similarity computation
- ✓ Self-exclusion (book doesn't recommend itself)
- ✓ Similarity scoring (similar books score higher)
- ✓ Performance benchmarks

## Configuration

Edit `.env` to customize:

```bash
RECOMMENDATIONS_TOP_K=3          # Default number of recommendations
TF_IDF_MIN_DF=2                  # Minimum document frequency
TF_IDF_MAX_FEATURES=1000         # Maximum vocabulary size
TF_IDF_NGRAM_RANGE=1,2           # N-gram range (1,2 = unigrams + bigrams)
RECOMMENDATION_CACHE_PATH=tfidf_cache.pkl  # Cache file location
```

## Troubleshooting

### No recommendations returned

**Possible causes**:
- Too few books in database (< 5)
- Books lack descriptions/metadata
- Min_df threshold too high

**Solutions**:
- Add more books with rich descriptions
- Lower `TF_IDF_MIN_DF` in config
- Check that books have genre and description fields

### Slow query performance

**Possible causes**:
- Cache not loaded
- Too many books (> 10,000)
- Large vocabulary size

**Solutions**:
- Ensure cache is being used
- Reduce `TF_IDF_MAX_FEATURES`
- Consider database indexing for book queries

### Poor recommendation quality

**Possible causes**:
- Insufficient book metadata
- Generic descriptions
- Incorrect feature weighting

**Solutions**:
- Enhance book descriptions
- Adjust feature weights in `recommendations.py`
- Tune TF-IDF parameters

---

**For more information**, see:
- `app/services/recommendations.py` - Core implementation
- `tests/unit/test_recommendations.py` - Unit tests
- `scripts/demo_recommendations.py` - Demo script
