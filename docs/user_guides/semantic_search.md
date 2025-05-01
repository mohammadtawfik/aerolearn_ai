# User Guide: Hybrid Semantic Search

## What is Hybrid Semantic Search?

Hybrid Semantic Search in AeroLearn AI lets you find relevant courses, modules, or lessons using a combination of:
- **Semantic search:** Finds content similar in meaning (even if keywords differ)
- **Keyword search:** Finds content with matching words or phrases

## Key Features

- **Permissive search:** Honors individual user permissions and visibility rules
- **Component targeting:** Limit search to courses, lessons, or any other content types
- **Customizable scoring:** Adjust result ranking to favor semantic or keyword matching
- **Deduplication:** Prevents the same record from appearing more than once
- **Tunable relevance:** Change the blend of semantic vs. keyword matching

## How to Use

1. **Search for a Topic**

   ```python
   results = searcher.search(
       "AI fundamentals",
       ["lesson"],
       context,
       user_id="student1"
   )
   ```

2. **Restrict to Specific Types**

   `targets=["course", "lesson"]` restricts results to just those types.

3. **Require Permission Filtering**

   - By default, your permissions are applied so you only see your content.
   - You may supply a custom permission filter function.

4. **Change Weights for Ranking**

   ```python
   results = searcher.search(
     "Neural networks",
     ["course", "lesson"],
     context,
     mode="hybrid",
     custom_weights={"semantic":0.8, "keyword":0.2}
   )
   ```

5. **Inspect Search Results**

   Each result contains:
   - `id` (unique content ID)
   - `agg_score` (final ranking score)
   - `source` ("semantic", "keyword", or "hybrid")
   - Content fields, e.g., title, description

6. **Tune the Search**

   For advanced tuning, refer to the API Docs (`/docs/api/search_api.md`).

## Best Practices

- Combine keyword and semantic for best relevance.
- Tune weights for use cases (semantic-heavy for open-topic, keyword-heavy for factual recall).
- Always provide relevant targets and user ID for best filtering.

## Troubleshooting

- “No results” usually means permission or an overly strict search type (try hybrid mode).
- Duplicates are auto-removed by ID, but different content with similar titles may still appear.

## More Info

For API integration, see: `/docs/api/search_api.md`