# AeroLearn AI Generated Documentation Site

## Component Interface Summary

### `app/core/auth/user_profile.py` — `UserProfile`

Represents the user's profile and identity attributes.

### `app/core/auth/user_profile.py` — `UserProfileManager`

Core logic for user profile management (CRUD, validation, bulk ops).

### `app/core/auth/authentication.py` — `AuthEvent`

Event representing authentication-related changes (login, logout, failure).

### `app/core/auth/authentication.py` — `AuthenticationProvider`

Interface for authentication providers.

### `app/core/auth/authentication.py` — `LocalAuthenticationProvider`

Simple authentication provider with in-memory user verification and event emission.
Replace with secure store/database integration as appropriate.

### `app/core/auth/authentication.py` — `MFAProvider`

Simple TOTP-like provider for MFA codes — 
**** WARNING: This is a DEMO implementation. NOT secure for production. ****
Replace with RFC 6238 compliant library for real deployments.

### `app/core/auth/authentication.py` — `AuthenticationService`

Main service interface for authentication logic.
Delegates authentication to configured providers.
Tracks the currently authenticated user's role for UI role-based navigation.

Methods:
    - authenticate(username, password): Authenticate user, returns UserProfile or None.
    - authenticate_admin(username, password, mfa_code): For admin logins with MFA.
    - logout(user_profile): Logs out the user.
    - enforce_permission(session, permission): Checks user permission (for admin area).
    - get_current_role(): Returns the current session's role (for UI navigation).
    - get_current_user(): Returns the current user profile or None.

### `app/core/auth/authentication.py` — `AuthSession`

Simple session object representing an authenticated user session.

### `app/core/auth/authentication.py` — `Authenticator`

Minimal authentication entrypoint for integration testing.
Provides a protocol-compliant interface required by integration and TDD tests.

### `app/core/auth/session.py` — `Session`

Represents an authenticated session.

### `app/core/auth/session.py` — `SessionManager`

Handles session creation, validation, and expiration.

### `app/core/auth/authorization.py` — `Permission`

Represents a single permission string, such as 'content.edit' or 'user.manage'.

### `app/core/auth/authorization.py` — `Role`

Represents a user role (e.g., student, professor, admin), with a set of permissions.
Supports role hierarchy (inheritance).

### `app/core/auth/authorization.py` — `UserPermissions`

Assigns roles and direct permissions to users (by user_id).

### `app/core/auth/authorization.py` — `AuthorizationManagerClass`

Central registry for roles, permissions, and user/role assignment.
Provides high-level APIs for assigning and checking permissions/roles.

### `app/core/auth/authorization.py` — `require_permission`

Decorator for functions/methods to enforce the required permission.
Expects the decorated function to accept a 'user_id' kwarg or positional argument.

### `app/core/db/migrations.py` — `create_all_tables`

Create all tables defined in the Base metadata.

### `app/core/db/migrations.py` — `drop_all_tables`

Drop all tables defined in the Base metadata.

### `app/core/db/migrations.py` — `list_tables`

List all tables in the database.

### `app/core/db/migrations.py` — `verify_schema`

Verify that the database schema matches the expected schema.

### `app/core/db/migrations.py` — `get_table_details`

Get detailed information about a specific table.

### `app/core/db/migrations.py` — `run_migration`

Run migration to specified version or latest.
This is a placeholder for future implementation with a proper migration tool.

### `app/core/db/db_events.py` — `_get_primary_key`

Helper to retrieve primary key(s) as a dict.

### `app/core/db/db_events.py` — `register_db_event_hooks`

Register all hooks for after_insert, after_update, after_delete
on all ORM models found in schema.Base registry.

### `app/core/db/local_cache.py` — `LocalCacheInvalidationPolicy`

Handles cache invalidation policies (time-based, manual, integrity).

### `app/core/db/local_cache.py` — `LocalCache`

Local cache storage supporting offline operation and prioritization.

Singleton is per-db_path for proper test isolation; .get() always rechecks expiration
and invalidates expired items every time.

### `app/core/db/sync_manager.py` — `RemoteSyncProvider`

Simulated remote store (would be replaced with actual DB/API client).

### `app/core/db/sync_manager.py` — `SyncManager`

Manage synchronization between the local cache and remote (cloud/server).
Detects and resolves conflicts. Handles offline/online mode.

### `app/core/db/course_admin.py` — `SimpleCourse`

Simple course model for testing without ORM dependencies

### `app/core/drive/file_operations.py` — `FileOperationError`

Custom exception type for file operations.

### `app/core/drive/metadata_inheritance_utilities.py` — `inherit_metadata`

For any field not present in item_metadata, inherit from parent_metadata.
If overwrite=True, parent_metadata always replaces item_metadata.

### `app/core/drive/metadata_store.py` — `MetadataStore`

Simple file-based persistence for demonstration.

### `app/core/drive/metadata_persistence_manager.py` — `MetadataStore`

Simple file-based persistence for demonstration.

### `app/core/ai/embedding.py` — `BaseEmbedder`

Abstract base class for content embedders.

### `app/core/ai/embedding.py` — `TextEmbedder`

Embeds plain text into a dense vector using simple bag-of-words on lowercase letters
for more consistent and testable similarity outputs.

### `app/core/ai/embedding.py` — `DocumentEmbedder`

Embeds a document (could be PDF, DOCX, etc.) by processing its text content.

### `app/core/ai/embedding.py` — `MultimediaEmbedder`

Embeds multimedia (video, audio, image) by converting metadata to text
and using the text embedder.

### `app/core/ai/embedding.py` — `EmbeddingGenerator`

EmbeddingGenerator is responsible for generating vector representations (embeddings) 
from input text or content.

This is the main API for creating embeddings in the AeroLearn AI system.

Usage:
    emb_gen = EmbeddingGenerator()
    vec = emb_gen.embed("example content")
    vec = emb_gen.embed({"type": "video", "title": "Learning AI"})  # multimedia

### `app/core/ai/content_similarity.py` — `SimilarityCalculator`

Provides static methods for common similarity metrics.

### `app/core/ai/content_similarity.py` — `ContentSimilarityCalculator`

Adapter API for project-wide content similarity calculations.
Usage:
    csc = ContentSimilarityCalculator()
    score = csc.similarity_score(vec_a, vec_b, metric='cosine')

### `app/core/ai/content_similarity.py` — `calculate_similarity`

Embeds and compares two pieces of content (text, document, multimedia).
Returns similarity score and match boolean (always Python bool).

### `app/core/ai/content_similarity.py` — `cross_content_similarity`

Given two lists (e.g. lessons from two courses), computes pairwise similarity 
and returns a score matrix and match flags (Python bool).

### `app/core/ai/content_similarity.py` — `get_content_recommendations`

Recommends the top-K most similar items from candidate_contents to target_content.
Returns strictly Python bool in all flags.

### `app/core/ai/content_similarity.py` — `ContentSimilarityEngine`

Unifies content similarity routines for the AeroLearn AI system.
Provides a high-level interface for computing similarities between content items.

Usage: 
    engine = ContentSimilarityEngine()
    similarities = engine.compute_similarities(content_list)

### `app/core/ai/preprocessing.py` — `ContentPreprocessor`

Performs basic content preprocessing for AI analysis.
Includes whitespace cleanup, case normalization, special char removal, etc.
Extend as needed for more advanced NLP tasks.

### `app/core/ai/vector_index.py` — `VectorIndex`

VectorIndex provides a simplified API for adding embeddings and querying similarity,
internally leveraging the VectorIndexManager.

### `app/core/ai/vector_index.py` — `get_vector_index`

Factory for creating a new VectorIndex.
Useful for both production (384+) and test (small dims).

### `app/core/ai/vector_index.py` — `add_content_embedding`

Add content embedding and associated metadata to the vector DB.

### `app/core/ai/vector_index.py` — `query_similar_content`

Find similar content using vector search, filter with metadata if needed.
Returns normalized results as dictionaries with 'score' and 'metadata' keys.
Always returns a list, never a scalar, even if empty.

### `app/core/ai/conversation.py` — `InMemoryConversationStore`

Pluggable (currently in-memory) session persistence.

### `app/core/ai/conversation.py` — `ConversationContext`

Tracks per-session dynamic memory/state.

### `app/core/ai/conversation.py` — `ConversationHistory`

Tracks user-bot conversation with privacy settings.

add_turn now accepts an optional 'metadata' field,
which can store extra dict information for each turn.

### `app/core/ai/conversation.py` — `ConversationState`

Full persistent snapshot for user session.

### `app/core/ai/conversation.py` — `ConversationManager`

Main orchestrator for conversational AI sessions.
Implements flow/component handler routing, privacy-aware state, and persistence.

### `app/core/ai/semantic_search.py` — `PermissionDenied`

Exception raised when a user doesn't have permission to access content

### `app/core/ai/semantic_search.py` — `HybridSemanticSearch`

Unified search interface combining keyword and semantic strategies,
supporting permission filtering and custom scoring/aggregation.

### `app/core/ai/concept_extraction.py` — `_normalize_term`

Basic lemmatization to normalize terms (e.g., plurals to singular form).

Args:
    term: The term to normalize
    
Returns:
    Normalized form of the term

### `app/core/ai/concept_extraction.py` — `normalize_to_ascii`

Remove accents/diacritics and lower-case.

Args:
    s: The string to normalize
    
Returns:
    ASCII-normalized lowercase string

### `app/core/ai/concept_extraction.py` — `Concept`

Represents an extracted concept (e.g., term, skill, entity).

### `app/core/ai/concept_extraction.py` — `ConceptExtractor`

Base class for concept extractors.

### `app/core/ai/concept_extraction.py` — `PatternConceptExtractor`

Extracts concepts from text using regex patterns.
For MVP: improved keyword/phrase extraction with extensibility hooks.
Extracts both compound phrases and their components.

### `app/core/ai/concept_extraction.py` — `DomainConceptExtractor`

Extracts concepts from a set of provided domain terms.
- Matches are accent/diacritic-insensitive (so schrodinger matches Schrödinger)
- Handles plurals, compounds, and hyphen-joined words robustly
- Only the canonical domain term spelling appears in result Concept names

### `app/core/ai/concept_extraction.py` — `extract_concept_relationships`

Identify relationships (content_id <-> concept) using the extractor.

Args:
    content_id: The identifier for the material (lesson, quiz, etc)
    text: The source text
    extractor: The concept extractor

Returns:
    List of (content_id, concept_name) tuples representing relationships

### `app/core/ai/resource_discovery.py` — `ResourceResult`

Standardized resource result format as expected by tests.

### `app/core/ai/resource_discovery.py` — `ResourceDiscoveryOrchestrator`

Coordinates resource discovery from multiple providers,
ensures deduplication, normalization, and compatibility with scoring/filtering logic.
Handles both single content and list of contents.
Always attempts fetch_resources first, then find_resources if available.

### `app/core/ai/resource_discovery.py` — `ResourceDiscovery`

Legacy class maintained for backward compatibility.

### `app/core/ai/prompt_engineering.py` — `PromptEngineering`

Main class handling prompt engineering workflow:
  - Template selection and variable substitution
  - Context merging
  - Prompt optimization (iterative improvement)
  - Response parsing

### `app/core/api/api_client.py` — `APIClientError`

Base exception for API client errors.

### `app/core/api/api_client.py` — `RateLimitExceeded`

Raised when API rate limits are exceeded.

### `app/core/api/api_client.py` — `APIClient`

Abstract base API client.
Provides error handling, rate limiting, basic request/response interface, and caching hooks.
Extend this class for each 3rd-party API client.

### `app/core/api/api_client.py` — `DeepSeekClient`

Concrete API client for DeepSeek services.

### `app/core/api/api_client.py` — `GoogleDriveClient`

Concrete API client for Google Drive services.

### `app/core/api/deepseek_client.py` — `DeepSeekClient`

Concrete API client for DeepSeek services.

### `app/core/api/google_drive_client.py` — `GoogleDriveClient`

Concrete API client for Google Drive services.

### `app/core/api/course_api.py` — `browse_courses`

Browse all courses.

### `app/core/api/course_api.py` — `search_courses`

Search courses by keyword.

### `app/core/api/course_api.py` — `request_enrollment`

Request enrollment in a course.

### `app/core/api/course_api.py` — `approve_enrollment`

Approve a pending enrollment request.

### `app/core/api/course_api.py` — `reject_enrollment`

Reject an enrollment request.

### `app/core/api/course_api.py` — `cancel_enrollment`

Cancel an enrollment request (by student).

### `app/core/api/course_api.py` — `get_enrollment_status`

Get current enrollment status for this user/course.

### `app/core/upload/upload_service.py` — `BackoffStrategy`

Implements exponential backoff with jitter for retries

### `app/core/upload/batch_controller.py` — `BatchStatus`

Status of a batch upload operation

### `app/core/upload/batch_controller.py` — `BatchEvent`

Event object for batch upload notifications

### `app/core/upload/batch_controller.py` — `BatchUploadListener`

Concrete base listener for batch upload event notifications.
Subclass or override `on_batch_event` as needed in tests or implementations.

### `app/core/upload/batch_controller.py` — `BatchUploadController`

Controller to manage batch uploads with aggregated progress and event reporting.
Accepts upload_service and validation_framework for test integration and future functionality.

### `app/core/upload/batch_controller.py` — `start_batch`

Start batch with optional metadata

### `app/core/upload/batch_controller.py` — `apply_metadata`

Apply metadata to all files in batch

Args:
    batch_id: Unique identifier for the batch
    metadata: Dictionary of metadata to apply

### `app/core/monitoring/metrics.py` — `track_learning_objective`

Track the degree of achievement for a specific learning objective by user.

:param user_id: User identifier
:param objective_id: Learning objective identifier
:param activities: List of activity logs relevant to the objective.
    Each activity should include: {"user_id":str, "objective_id":str, "completed":bool}
:return: Completion ratio [0, 1]

### `app/core/monitoring/metrics.py` — `monitor_time_on_task`

Monitor total time on task for a user.

:param user_id: User identifier
:param activity_logs: List of logs with start/end times
    Each log should include: {"user_id":str, "start":ISO 8601 str, "end":ISO 8601 str}
:return: Total duration on-task as timedelta

### `app/core/monitoring/metrics.py` — `calculate_completion_rate`

Calculate overall module completion rate for the user.

:param user_id: User identifier
:param module_ids: List of curriculum module IDs
:param completion_logs: List of logs, each with {"user_id":str, "module_id":str, "completed":bool}
:return: Fraction completed [0, 1]

### `app/core/monitoring/metrics.py` — `analyze_performance_trends`

Analyze trends in student performance over time.

:param user_id: User identifier
:param performance_history: List of score/timestamp dicts
   Each entry should include: {"user_id":str, "score":float, "timestamp": ISO 8601 str}
:return: Dict with trend summary (e.g., "improving", "declining", "stable", plus details)

### `app/core/monitoring/metrics.py` — `assessment_performance_analytics`

Summarize assessment performance for user: mean, min, max, count.
Each record must have: {"user_id", "score"}

### `app/core/monitoring/metrics.py` — `engagement_score`

Sum engagement points for a user by interaction type.
- view: 1pt
- submit_quiz: 5pt
- post_forum: 2pt
Unknown types: 0pt

### `app/core/monitoring/metrics.py` — `competency_mapping`

Return set of competency_id values achieved by user; achieved if score >= threshold.
Assessments: [{"user_id", "score", "competency_id", "threshold"}]

### `app/core/monitoring/metrics.py` — `comparative_cohort_analytics`

Compare two cohorts by average progress/engagement.
Each group: list of {"user_id", "progress"} dict
cohort_higher: 1 if first is higher, 2 if second is higher, 0 if equal

### `app/core/monitoring/metrics.py` — `save_analytics_result`

Save analytics results for a student to in-memory storage.
Used for integration testing of learning analytics.

:param student_id: Student identifier
:param data: Analytics data to store

### `app/core/monitoring/metrics.py` — `retrieve_analytics_result`

Retrieve previously saved analytics results for a student.

:param student_id: Student identifier
:return: Stored analytics data or empty dict if not found

### `app/core/monitoring/metrics.py` — `clear_analytics_storage`

Clear all stored analytics results.
Useful for test setup/teardown.

### `app/core/monitoring/metrics.py` — `ProgressMetrics`

Records user progress per course and provides progress event interface.
Designed for test-driven, in-memory use; expandable for database backing.

### `app/core/monitoring/metrics.py` — `AnalyticsEngine`

Minimal stub: Analytics system that queries progress from ProgressMetrics.
Meant to satisfy TDD and integration test interface; no persistence.

### `app/core/monitoring/metrics.py` — `PerformanceAnalyzer`

Analyzes performance metrics for system components.
Protocol-compliant implementation supporting per-component metric history, 
cross-component transaction flow/timing, and real bottleneck alerting.

### `app/core/monitoring/notification_center.py` — `NotificationCenter`

Stub implementation of NotificationCenter that maintains the same interface
but with simplified functionality for testing purposes.

### `app/core/monitoring/pattern_detection.py` — `ComponentStatus`

Represents the operational status of a monitoring component.

### `app/core/monitoring/pattern_detection.py` — `HealthReport`

Aggregates component statuses into a comprehensive health report.

### `app/core/monitoring/pattern_detection.py` — `detect_activity_sequences`

Analyze order and transitions in user learning events.
Returns: frequent patterns, sequences found

### `app/core/monitoring/pattern_detection.py` — `detect_resource_utilization`

Detect overall and per-type resource usage from logs.
Returns: summary statistics per resource

### `app/core/monitoring/pattern_detection.py` — `infer_study_habits`

Identify study habit patterns (e.g., cramming, steady, random).
Returns: inferred habit, confidence

### `app/core/monitoring/pattern_detection.py` — `classify_learning_style`

Classify the learning style: e.g., 'visual', 'auditory', 'kinesthetic', 'mixed'.

### `app/core/monitoring/pattern_detection.py` — `run_pattern_detection`

Analyze raw progress records and return detected patterns (e.g., at-risk).

Args:
    progress_records: List of student progress data records
    
Returns:
    List of detected patterns with risk assessments

### `app/core/monitoring/pattern_detection.py` — `aggregate_learning_data`

Aggregate and combine learning activity data from multiple models/components.

Args:
    records: Raw learning activity records
    
Returns:
    Aggregated analytics data including breakdown by student and activity

### `app/core/monitoring/pattern_detection.py` — `should_trigger_intervention`

Decide if intervention should be triggered based on analytics.

Args:
    analytics: Aggregated analytics data including patterns
    
Returns:
    Boolean indicating if intervention is needed

### `app/core/monitoring/pattern_detection.py` — `get_intervention_recommendations`

Generate personalized intervention recommendations for a specific student.

Args:
    student_id: The ID of the student
    analytics: Aggregated analytics data
    
Returns:
    Intervention recommendations or None if not needed

### `app/core/monitoring/interventions.py` — `early_warning_indicator`

Return list of at-risk students based on provided progress records.
Rule: any student with completion_rate < 0.3 is at risk.

### `app/core/monitoring/interventions.py` — `recommend_resources`

Suggest targeted resources (resource IDs) based on student and analytics.
General rule:
- For any topic in analytics where value is 'low', recommend 'resource_{topic}1'
- For any topic in student_profile.needs, recommend 'resource_{topic}_advanced'

### `app/core/monitoring/interventions.py` — `suggest_learning_path`

Generate an ordered list of learning activity IDs as a personalized path.
For this iteration, simply map each 'math' or 'science' objective
to 'lesson_math1' or 'lesson_science1', preserving order.

### `app/core/monitoring/interventions.py` — `notify_professor_at_risk_students`

Notify professor with data on at-risk students.
Attaches the notification to the professor object for testability.

### `app/core/monitoring/interventions.py` — `create_intervention`

Stub: Create an intervention for the given student based on a pattern.
Returns a dictionary representing the intervention.
Includes a 'type' field as required for pipeline integration tests.

### `app/core/monitoring/integration_monitor.py` — `IntegrationMonitor`

Implements service/integration health monitoring, transaction audit/history,
and alerting, as defined in the protocol docs.

### `app/core/monitoring/resource_registry.py` — `ResourceRegistry`

Resource Registry for tracking, assignment, availability, and conflict analysis.
Fulfills requirements of /docs/development/day20_plan.md (Task 3.7.3) and all protocols.

### `app/core/monitoring/ServiceHealthDashboard_Class.py` — `StatusRecord`

Standardized record for component status tracking and audit logging.
Used for health dashboard, status history, and compliance reporting.

### `app/core/monitoring/ServiceHealthDashboard_Class.py` — `ServiceHealthDashboard`

Protocol-compliant Service Health Dashboard.
Monitors and visualizes component/service health across the AeroLearn system.

Features:
- Real-time status tracking and dependency visualization
- Historical status records and audit trail
- Health alerting with configurable callbacks
- Component dependency graph and topology visualization

Test compatibility:
- status_for(name) returns the ComponentState enum
- get_all_component_statuses returns a dict mapping name to ComponentStatus objects
- Properly distinguishes between DEGRADED/DOWN/FAILED states for test assertions

Health Alert Callbacks:
- Use `register_alert_callback(cb)` to register alert callbacks
- On a transition to DEGRADED/DOWN/FAILED, all registered callbacks are invoked with (component_id, new_state)

Real-Time Update Callbacks:
- Callbacks registered with watch_component are fired when component state changes
- get_all_component_statuses provides real-time status for all components

Metrics Support:
- update_component_status accepts optional metrics dict for audit/dashboard/test compliance
- get_status_history retrieves full status history for a component

### `app/core/monitoring/ServiceHealthDashboard_Class.py` — `_reset_for_test`

Reset (clear) the singleton for test isolation.
Safe for pytest/integration use: resets registry as well.

### `app/core/extraction/structured_data_extractor.py` — `StructuredDataExtractor`

Extracts tabular data from PDF, DOCX, and PPTX files.
Only basic diagram detection is supported (future work can extend).

### `app/core/extraction/text_extractor.py` — `TextExtractor`

Extracts raw text from various document formats including PDF, DOCX, PPTX, and TXT.
Falls back to OCR with tesseract or PIL if necessary for image-based content.

Provides robust support for text files with various encodings and error handling.

### `app/core/extraction/multimedia_metadata_extractor.py` — `MultimediaMetadataExtractor`

Extracts metadata from images, audio, and video files as much as supported.

### `app/core/search/base_search.py` — `SearchResult`

Dict with required fields for all search results:
id: str     - Unique result identifier
score: float- Raw relevance score
source: str - Which backend provided this result
data: dict  - Arbitrary additional result data

### `app/core/search/base_search.py` — `SearchBackend`

Base interface for all search backends.

### `app/core/search/keyword_search.py` — `KeywordSearch`

Concrete implementation of a keyword-based search backend.

### `app/core/search/semantic_backend.py` — `embed_text`

Improved dummy embedding: Bag-of-characters (lowercase a-z and space).
Returns a fixed 27-dimensional vector (frequency of each a-z and ' ').
This approach gives positive similarity for overlapping terms, unlike character hash.

### `app/core/search/semantic_backend.py` — `SemanticSearchBackend`

Embedding-based semantic search backend.
Uses naive bag-of-characters dummy embedding for demonstration/testing.
Replace embed_text with real embedding model for production use.

### `app/core/search/result_aggregation.py` — `aggregate_and_deduplicate_results`

Combines results from multiple backends, dedupes using ID, and fuses scores.
Returns unified list sorted by hybrid score.

### `app/core/search/permissions.py` — `filter_by_permission`

Returns only items user is allowed to see based on permissions.
Placeholder: expects each result to have 'data' dict with 'permissions' list.

### `app/core/relationships/knowledge_graph.py` — `Node`

Represents a concept or content item in the knowledge graph.

### `app/core/relationships/knowledge_graph.py` — `Edge`

Represents a relationship between two nodes.

### `app/core/relationships/knowledge_graph.py` — `KnowledgeGraph`

Simple in-memory representation of a knowledge graph.
Nodes = concepts/content items; Edges = relationships.
Supports visualization and navigation of relationships.

-- API NOTE --
Use add_relationship() as the canonical way to add relationships.
add_edge() is also provided for generality and legacy support.

`get_neighbors`, `get_related`, and similar will return node IDs (strings) by default,
matching test expectations and typical graph API usage.
Pass return_objects=True to get Node instances instead.

### `app/core/relationships/relationship_finder.py` — `RelationshipFinder`

Finds relationships (prerequisite, reference, related) between concepts or content nodes.

### `app/core/relationships/navigation.py` — `RelationshipNavigator`

Supports finding recommended next concepts/nodes based on relationships.
Provides navigation and recommendation utilities over the knowledge graph.

NOTE: All public methods consistently accept *either* Node or node id (str) as input,
and always return Node objects (not ids), unless otherwise documented.

### `app/core/relationships/visualization.py` — `export_graph_as_json`

Exports the graph to a dict structure ready for JSON serialization.
UI/frontend can consume this for visualization.

### `app/core/relationships/relationship_extractor.py` — `ConceptRelationship`

Represents a relationship between two concepts or between a concept and a content object.

### `app/core/relationships/relationship_extractor.py` — `RelationshipExtractor`

Extracts explicit and implicit relationships between concepts or content.

### `app/core/external_resources/providers.py` — `BaseResourceProvider`

Abstract external resource provider.
Subclasses implement fetch_resources(course).

### `app/core/external_resources/providers.py` — `MockProvider`

A mock provider returning deterministic, static resources for use in tests.
Used for integration and unit tests to ensure predictable results.

### `app/core/external_resources/scoring.py` — `score_resource`

Compute a relevance/quality score between this resource and the course.
This can be as sophisticated as needed; for now, use title similarity and fallback.

### `app/core/external_resources/scoring.py` — `ResourceScorer`

Class encapsulating resource scoring and filtering logic.
Used by resource discovery orchestrators and integration tests.

### `app/core/external_resources/workflow.py` — `integrate_resources_with_content`

Embed external resource links in content metadata, database, or user-facing recommendations.
Extend this function as required by the platform's data model.

### `app/core/prompts/template_engine.py` — `PromptTemplateEngine`

Handles registration and rendering of prompt templates, variable interpolation, and context merging.

### `app/core/prompts/optimizers.py` — `PromptOptimizer`

Applies optimization heuristics to improve prompt efficacy.
For Task 14.2, behavior is pluggable and can be extended.

### `app/core/integration/integration_coordinator.py` — `IntegrationCoordinator`

High-level integration controller; expose unified API for app core.

### `app/core/enrollment/enrollment_service.py` — `EnrollmentService`

Service class for managing course enrollments and enrollment requests.
Uses in-memory store for illustration—replace with DB/session as needed.

### `app/core/assessment/session_manager.py` — `GradingEngine`

Handles grading of assessment sessions

### `app/core/assessment/grading.py` — `GradingEngine`

Handles grading of assessment questions and sessions.

### `app/core/assessment/manual_grading.py` — `ManualGradingService`

Service-layer class for managing manual grading workflow:
- Assigning submissions to professors for grading
- Grading individual answers with a rubric (returns grade, feedback)
- Handling batch grading
- Notifying or recording graded assignments/feedback
This enables test_assessment_engine_day17 and fits architecture pattern for Engines/Services.

### `app/core/assessment/feedback.py` — `FeedbackService`

Service façade for feedback delivery, notification, and analytics,
coordinating internal FeedbackEngine and providing a stable API for integration and tests.

### `app/core/project_management/milestone_tracker.py` — `MilestoneRegistry`

Registry and manager for system/project milestones.

- Register milestones (multi-component capable)
- Set/query dependencies (dependency graph)
- Calculate and retrieve milestone progress
- Audit history, protocol-compliant error/cycle protection, risk

### `integrations/interfaces/base_interface.py` — `InterfaceVersion`

Helper class for managing interface versioning.

This class follows semantic versioning principles where:
- MAJOR version changes indicate incompatible API changes
- MINOR version changes indicate backwards-compatible functionality additions
- PATCH version changes indicate backwards-compatible bug fixes

### `integrations/interfaces/base_interface.py` — `MethodSignature`

Class for representing and validating method signatures.

This class captures the signature information of a method, including
parameter types and return type annotations, to enable validation when
implementing interfaces.

### `integrations/interfaces/base_interface.py` — `InterfaceMethod`

Decorator for interface methods that captures signature information.

### `integrations/interfaces/base_interface.py` — `InterfaceError`

Base exception for interface-related errors.

### `integrations/interfaces/base_interface.py` — `InterfaceImplementationError`

Exception raised when an interface is implemented incorrectly.

### `integrations/interfaces/base_interface.py` — `InterfaceRegistryError`

Exception raised for interface registration errors.

### `integrations/interfaces/base_interface.py` — `InterfaceVersionError`

Exception raised for interface version errors.

### `integrations/interfaces/base_interface.py` — `BaseInterface`

Base class for all interface contracts in the system.

### `integrations/interfaces/base_interface.py` — `InterfaceImplementation`

Decorator for classes that implement interfaces.

This decorator validates that a class correctly implements all
the interfaces it claims to implement.

### `integrations/interfaces/base_interface.py` — `InterfaceRegisteredEvent`

Event fired when an interface is registered.

### `integrations/interfaces/base_interface.py` — `register_all_interfaces`

Register all interfaces defined in the system.

This function scans all subclasses of BaseInterface and registers them.
It should be called once during system initialization.

### `integrations/interfaces/content_interface.py` — `ContentType`

Enumeration of supported content types.

### `integrations/interfaces/content_interface.py` — `ContentFormat`

Enumeration of specific content formats.

### `integrations/interfaces/content_interface.py` — `ContentMetadata`

Class for content metadata with standard fields and custom properties.

### `integrations/interfaces/content_interface.py` — `ContentReference`

Reference to content that can be resolved by content providers.

### `integrations/interfaces/content_interface.py` — `ContentSearchResult`

Result from a content search operation.

### `integrations/interfaces/content_interface.py` — `ContentProviderInterface`

Interface for components that provide access to content.

Content providers are responsible for retrieving and storing content,
but not for processing or transforming it.

### `integrations/interfaces/content_interface.py` — `ContentSearchInterface`

Interface for components that provide content search capabilities.

### `integrations/interfaces/content_interface.py` — `ContentIndexerInterface`

Interface for components that index content for search.

### `integrations/interfaces/content_interface.py` — `ContentProcessorInterface`

Interface for components that process and transform content.

### `integrations/interfaces/content_interface.py` — `ContentAnalyzerInterface`

Interface for components that analyze content for insights.

### `integrations/interfaces/storage_interface.py` — `StorageScope`

Defines the scope/visibility of stored data.

### `integrations/interfaces/storage_interface.py` — `StoragePermission`

Permission levels for stored items.

### `integrations/interfaces/storage_interface.py` — `SyncStatus`

Synchronization status for stored items.

### `integrations/interfaces/storage_interface.py` — `StorageItem`

Represents a storage item (file or folder) with metadata.

### `integrations/interfaces/storage_interface.py` — `SyncConflict`

Represents a synchronization conflict between local and remote versions.

### `integrations/interfaces/storage_interface.py` — `SyncProgress`

Represents the progress of a synchronization operation.

### `integrations/interfaces/storage_interface.py` — `StorageProviderInterface`

Interface for components that provide storage capabilities.

### `integrations/interfaces/storage_interface.py` — `SynchronizationInterface`

Interface for components that synchronize content between storage providers.

### `integrations/interfaces/storage_interface.py` — `StorageQuotaInterface`

Interface for components that manage storage quotas.

### `integrations/interfaces/storage_interface.py` — `StoragePermissionInterface`

Interface for components that manage storage permissions.

### `integrations/interfaces/storage_interface.py` — `FileStreamingInterface`

Interface for components that provide file streaming capabilities.

### `integrations/interfaces/storage_interface.py` — `StorageInterface`

Abstract interface for storage service integration.
All storage connectors should implement this interface.

This simplified interface is used by orchestration and integration components
that need basic storage operations without the full complexity of the
specialized storage interfaces above.

### `integrations/interfaces/ai_interface.py` — `AIModelType`

Types of AI models used in the system.

### `integrations/interfaces/ai_interface.py` — `AIModelCapability`

Specific capabilities that AI models might provide.

### `integrations/interfaces/ai_interface.py` — `AIProviderType`

Types of AI providers.

### `integrations/interfaces/ai_interface.py` — `AIModelMetadata`

Metadata about an AI model.

### `integrations/interfaces/ai_interface.py` — `AIRequest`

Base class for AI requests.

### `integrations/interfaces/ai_interface.py` — `TextGenerationRequest`

Request for text generation.

### `integrations/interfaces/ai_interface.py` — `EmbeddingRequest`

Request for text embedding.

### `integrations/interfaces/ai_interface.py` — `AIResponse`

Base class for AI responses.

### `integrations/interfaces/ai_interface.py` — `TextGenerationResponse`

Response from text generation.

### `integrations/interfaces/ai_interface.py` — `EmbeddingResponse`

Response from text embedding.

### `integrations/interfaces/ai_interface.py` — `AIModelProviderInterface`

Interface for components that provide access to AI models.

### `integrations/interfaces/ai_interface.py` — `ContentAnalysisInterface`

Interface for AI components that analyze educational content.

### `integrations/interfaces/ai_interface.py` — `LearningAssistantInterface`

Interface for AI components that provide learning assistance.

### `integrations/interfaces/ai_interface.py` — `PersonalizationInterface`

Interface for AI components that provide personalized recommendations.

### `integrations/interfaces/ai_interface.py` — `AIUsageTrackingInterface`

Interface for components that track AI usage and costs.

### `integrations/interfaces/ai_interface.py` — `register_ai_interfaces`

Register all AI interfaces.

This function should be called during system initialization.

### `integrations/registry/dependency_tracker.py` — `CircularDependencyError`

Exception raised when a circular dependency is detected.

### `integrations/registry/dependency_tracker.py` — `DependencyTracker`

Utility for tracking and analyzing dependencies between components.

This class provides methods for validating dependency relationships,
detecting circular dependencies, and determining optimal initialization
order for components.

### `integrations/registry/component_registry.py` — `Component`

Protocol-compliant component for registry and service health monitoring.

### `integrations/registry/component_registry.py` — `ComponentRegistry`

Central registry for AeroLearn AI system components.

Protocol-compliant implementation for service health monitoring and dependency tracking.
Provides .components dict and dependency graph for dashboard integration.

### `integrations/registry/interface_registry.py` — `InterfaceDefinitionError`

Exception raised when an interface is improperly defined.

### `integrations/registry/interface_registry.py` — `InterfaceImplementationError`

Exception raised when an interface is improperly implemented.

### `integrations/registry/interface_registry.py` — `Interface`

Base class for all interfaces in the system.

Interfaces define the contract that components must fulfill to provide
certain functionality to other components.

### `integrations/registry/interface_registry.py` — `InterfaceRegisteredEvent`

Event fired when an interface is registered.

### `integrations/registry/interface_registry.py` — `InterfaceRegistry`

Registry for interfaces in the system.

This class is implemented as a singleton to ensure there is only one
interface registry in the application.

### `integrations/registry/interface_registry.py` — `implements`

Decorator to mark a class as implementing an interface.

This decorator validates that the class correctly implements the interface
and registers this information with the component registry.

Args:
    interface_cls: The interface class that is implemented
    
Returns:
    Decorator function
    
Raises:
    InterfaceImplementationError: If the class does not correctly implement the interface

### `integrations/events/event_types.py` — `EventType`

General event type enumeration for core system/event bus usage.
Provides a centralized enum for all event types across categories.

For organizational clarity, category-specific event type classes
like SystemEventType, ContentEventType, etc. are also available.

### `integrations/events/event_types.py` — `EventPriority`

Event priority levels for determining handling order.

### `integrations/events/event_types.py` — `EventCategory`

Categories for grouping related events.

### `integrations/events/event_types.py` — `Event`

Base class for all events in the system.

### `integrations/events/event_types.py` — `SystemEvent`

System-level events related to application lifecycle and operations.

### `integrations/events/event_types.py` — `ContentEvent`

Events related to educational content operations.

### `integrations/events/event_types.py` — `UserEvent`

Events related to user actions and profile changes.

### `integrations/events/event_types.py` — `AIEvent`

Events related to AI operations and intelligence.

### `integrations/events/event_types.py` — `BatchEvent`

Events related to batch processing operations.

### `integrations/events/event_types.py` — `UIEvent`

Events related to user interface interactions.

### `integrations/events/event_types.py` — `EnrollmentEvent`

Events related to course enrollment processes.

### `integrations/events/event_types.py` — `SystemEventType`

Common system event type constants.

### `integrations/events/event_types.py` — `ContentEventType`

Common content event type constants.

### `integrations/events/event_types.py` — `UserEventType`

Common user event type constants.

### `integrations/events/event_types.py` — `AIEventType`

Common AI event type constants.

### `integrations/events/event_types.py` — `BatchEventType`

Common batch processing event type constants.

### `integrations/events/event_types.py` — `EnrollmentEventType`

Common enrollment event type constants.

### `integrations/events/event_subscribers.py` — `EventFilter`

EventFilter selects which events a subscriber is interested in 
by event type(s), category(ies), and minimum priority.

### `integrations/events/event_subscribers.py` — `AcceptAllEventFilter`

Default event filter that accepts all events.

### `integrations/events/event_subscribers.py` — `CompositeEventFilter`

Accepts events if any of the provided filters accept them.

### `integrations/events/event_subscribers.py` — `EventSubscriber`

Abstract base class for components that subscribe to events from the EventBus.

Subscribers implement the on_event method to handle events they are interested in.
Optionally, they may provide an event_filter property for advanced filtering.

### `integrations/events/event_subscribers.py` — `LoggingEventSubscriber`

Example event subscriber that logs all received events.

### `integrations/events/event_subscribers.py` — `CallbackEventSubscriber`

Event subscriber that uses a provided callback function for event processing.
Optionally, an EventFilter can be provided to filter which events to receive.

### `integrations/events/event_bus.py` — `EventBus`

Central event bus for the AeroLearn AI system.

This class implements the Singleton pattern to ensure there is only one
event bus instance in the application.

### `integrations/monitoring/integration_health.py` — `HealthStatus`

Health status levels for components and integrations.

### `integrations/monitoring/integration_health.py` — `HealthMetricType`

Types of health metrics that can be collected.

### `integrations/monitoring/integration_health.py` — `HealthMetric`

A single health metric measurement.

### `integrations/monitoring/integration_health.py` — `HealthEvent`

Event fired when a significant health status change occurs.

### `integrations/monitoring/integration_health.py` — `HealthProvider`

Interface for components that provide health information.

### `integrations/monitoring/integration_health.py` — `IntegrationHealthError`

Exception raised for errors in the integration health system.

### `integrations/monitoring/integration_health.py` — `IntegrationHealth`

Central system for tracking integration health across components.

This class collects health metrics from components, detects health status
changes, and provides visualization data for monitoring interfaces.
It also supports real-time notifications of health status changes through
a listener pattern.

### `integrations/monitoring/integration_health.py` — `IntegrationMonitor`

Monitors integration points for transaction success, performance, and failures.

This class provides methods to log transactions, report failures, and retrieve
performance statistics for integration points. It also supports real-time
status notifications through a listener pattern.

### `integrations/monitoring/integration_health.py` — `IntegrationPointRegistry`

Registry for integration points in the system.

This class maintains a registry of all integration points and provides
methods to register and retrieve them. It also supports notifications
when integration points are registered or updated.

### `integrations/monitoring/component_status.py` — `StatusSeverity`

Severity levels for component status changes.

### `integrations/monitoring/component_status.py` — `StatusChangeEvent`

Event fired when a component's status changes.

### `integrations/monitoring/component_status.py` — `ComponentStatusProvider`

Interface for components that provide status information.

### `integrations/monitoring/component_status.py` — `ComponentStatus`

Represents the status of a component at a specific point in time.

### `integrations/monitoring/component_status.py` — `StatusHistoryEntry`

A historical status entry for a component.

### `integrations/monitoring/component_status.py` — `ComponentStatusTracker`

System for tracking component status changes over time.

This class maintains current status for all registered components,
records status history, and generates events for status changes.

### `integrations/monitoring/transaction_logger.py` — `TransactionStage`

Stages of a transaction lifecycle.

### `integrations/monitoring/transaction_logger.py` — `TransactionEvent`

Event fired when a transaction changes stage.

### `integrations/monitoring/transaction_logger.py` — `TransactionError`

Exception raised for errors in transaction processing.

### `integrations/monitoring/transaction_logger.py` — `Transaction`

Represents a cross-component transaction.

A transaction is a logical unit of work that may involve multiple
components. This class tracks the flow of a transaction through
the system and provides status tracking and timing information.

### `integrations/monitoring/transaction_logger.py` — `TransactionContext`

Context manager for transaction handling.

Makes it easy to use transactions in with statements, handling
start, completion, and error conditions automatically.

### `integrations/monitoring/transaction_logger.py` — `TransactionLogger`

System for logging and tracking cross-component transactions.

This class maintains an in-memory record of recent transactions and
provides utilities for creating, updating, and retrieving transaction
information. It can also persist transactions to external storage.

### `integrations/monitoring/component_status_adapter.py` — `SimpleComponentStatusProvider`

Simple adapter between a Component and ComponentStatusProvider interface.
Used to allow status tracking of registry-registered components.

Always maintains a live reference to the component to ensure state changes
are immediately reflected.

### `integrations/monitoring/component_status_adapter.py` — `ComponentStatus`

Represents the operational status of a monitored component.
Guarantees that error_message is never None.

### `integrations/monitoring/component_status_adapter.py` — `EnhancedComponentStatusTracker`

Enhanced version of ComponentStatusTracker that ensures faithful propagation
of ComponentState enum values.

Designed for explicit dependency injection to ensure test isolation.

Provides methods for test isolation and proper component unregistration.

### `integrations/monitoring/component_status_adapter.py` — `ComponentRegistry`

Implementation of ComponentRegistry with dependency tracking support.

Designed for explicit instantiation to ensure test isolation.

### `integrations/monitoring/component_status_adapter.py` — `make_registry`

Create a new ComponentRegistry instance.

### `integrations/monitoring/component_status_adapter.py` — `make_tracker`

Create a new EnhancedComponentStatusTracker instance.

Args:
    registry: Optional ComponentRegistry instance to use for dependency tracking

### `integrations/monitoring/component_status_adapter.py` — `clear_all_status_tracking`

Clear all status tracking data for test isolation.
Clears both the registry and status tracker.

Usage in tests:

In your pytest/conftest.py or at start of every test, add:

import integrations.monitoring.component_status_adapter as cs_adapter

@pytest.fixture(autouse=True)
def reset_dashboard_state_and_tracking():
    cs_adapter.clear_all_status_tracking()

This ensures all state is wiped between tests.

### `integrations/monitoring/component_status_adapter.py` — `reset_tracking`

Reset tracking for specific instances or the default ones.

Args:
    status_tracker: The status tracker to reset, or None to use the default
    registry: The registry to reset, or None to use the default

### `integrations/monitoring/component_status_adapter.py` — `register_with_status_tracker`

Register a component with the status tracker.
This function allows core components to be registered with the monitoring system
without requiring core to directly import monitoring.

Protocol: Passes 'state' (not 'status') to dashboard as per service health protocol.
Always ensures the global SYSTEM_STATUS_TRACKER is updated regardless of provided instances.

Args:
    component: The component to register for status tracking
    system_status_tracker: Optional status tracker to use, defaults to SYSTEM_STATUS_TRACKER
    registry: Optional registry to use, defaults to COMPONENT_REGISTRY_SINGLETON

### `integrations/monitoring/component_status_adapter.py` — `get_system_status_tracker`

Get the default instance of the system status tracker

### `integrations/monitoring/component_status_adapter.py` — `get_component_registry`

Get the default instance of the component registry

### `integrations/monitoring/component_status_adapter.py` — `ServiceHealthDashboard`

Dashboard for monitoring component health with explicit dependency injection.

### `integrations/monitoring/component_status_adapter.py` — `unregister_from_status_tracker`

Unregister a component from the status tracker.
This function allows components to be properly removed from monitoring.

Args:
    component_id: The ID of the component to unregister
    system_status_tracker: Optional status tracker to use, defaults to SYSTEM_STATUS_TRACKER

### `integrations/monitoring/component_status_adapter.py` — `ComponentStatusAdapter`

Adapter for ServiceHealthDashboard status reporting, notifications, and test interfaces.
Bridges between ServiceHealthDashboard and ComponentRegistry, enforcing the Service Health Protocol.
Propagates component state changes, enables legacy and alert callbacks, ensures test and production compliance.

Implements status provider registry as required by the test protocol.

Acts as a singleton to maintain global state across all contexts.

Protocol-compliant with Service Health Protocol as documented in /docs/architecture/service_health_protocol.md

### `integrations/monitoring/component_status_adapter.py` — `_reset_for_test`

Reset all component state for SYSTEM_STATUS_TRACKER (TDD integration)
This function is called by test frameworks to ensure clean state between tests.

### `integrations/monitoring/component_status_adapter.py` — `get_default_adapter`

Get the default ComponentStatusAdapter instance

### `integrations/monitoring/component_status_adapter.py` — `update_component_status`

Protocol-compliant function to update a component's status.
Uses the global SYSTEM_STATUS_TRACKER to ensure proper propagation to dashboard and listeners.

Protocol: Uses 'state' parameter as per service health protocol.

Args:
    component_id: The ID of the component to update
    state: The new state of the component, or None to use component's current state
    details: Optional details/metrics about the component's status
    
Returns:
    True if the update was successful, False otherwise

### `integrations/week2/orchestrator.py` — `Week2Orchestrator`

Main orchestrator for Week 2 integration efforts.


---

## Protocol Documentation

- [api/service_health_protocol.md](../api/service_health_protocol.md)
- [architecture/dependency_tracking_protocol.md](../architecture/dependency_tracking_protocol.md)
- [architecture/health_monitoring_protocol.md](../architecture/health_monitoring_protocol.md)
- [architecture/service_health_protocol.md](../architecture/service_health_protocol.md)

---

## API Documentation

- [api/assessment_delivery_workflow.md](../api/assessment_delivery_workflow.md)
- [api/batch_content_metadata_api.md](../api/batch_content_metadata_api.md)
- [api/batch_content_metadata_examples.md](../api/batch_content_metadata_examples.md)
- [api/batch_operations.md](../api/batch_operations.md)
- [api/content_similarity_api.md](../api/content_similarity_api.md)
- [api/course_enrollment_api.md](../api/course_enrollment_api.md)
- [api/course_management_api.md](../api/course_management_api.md)
- [api/feature_development_tracker.md](../api/feature_development_tracker.md)
- [api/feedback_format_specifications.md](../api/feedback_format_specifications.md)
- [api/grading_rule_specifications.md](../api/grading_rule_specifications.md)
- [api/interventions_api.md](../api/interventions_api.md)
- [api/manual_grading_procedures.md](../api/manual_grading_procedures.md)
- [api/metadata_schema_and_extension_points.md](../api/metadata_schema_and_extension_points.md)
- [api/milestone_tracker.md](../api/milestone_tracker.md)
- [api/notification_api.md](../api/notification_api.md)
- [api/progress_metrics.md](../api/progress_metrics.md)
- [api/prompt_templates.md](../api/prompt_templates.md)
- [api/resource_allocation_api.md](../api/resource_allocation_api.md)
- [api/resource_discovery_api.md](../api/resource_discovery_api.md)
- [api/search_api.md](../api/search_api.md)
- [api/student_dashboard_widgets.md](../api/student_dashboard_widgets.md)
- [api/tagging_system.md](../api/tagging_system.md)
- [api/upload_system_api.md](../api/upload_system_api.md)
- [api/user_management_api.md](../api/user_management_api.md)
- [api/vector_db_api.md](../api/vector_db_api.md)
- [api/week2_api.md](../api/week2_api.md)

---

## Documentation Index Crosscheck

### ❗ Missing in Scan (Listed in doc_index.md, not found in scan):
- docs/architecture/integration_architecture.md
- docs/architecture/course_structure.md
- docs/api/milestone_tracker.md
- docs/user_guides/testing_procedures.md
- docs/api/resource_discovery_api.md
- docs/user_guides/prompt_engineering.md
- docs/ui/professor_upload_widget_api.md
- docs/api/course_management_api.md
- docs/user_guides/student_dashboard_features.md
- docs/api/upload_system_api.md
- docs/api/content_similarity_api.md
- docs/architecture/admin_security.md
- docs/api/user_management_api.md
- docs/development/day22_plan.md
- docs/development/day31_plan.md
- docs/api/batch_content_metadata_examples.md
- docs/api/week2_api.md
- docs/user_guides/content_analysis_workflows.md
- docs/index.md
- docs/development/day21_plan.md
- docs/development/day28_plan.md
- docs/user_guides/semantic_search.md
- docs/development/day13_plan.md
- docs/architecture/system_monitoring.md
- docs/ui/content_viewer_extension.md
- docs/api/student_dashboard_widgets.md
- docs/doc_index.md
- docs/development/sprint_plan.md
- docs/development/integration_test_documentation.md
- docs/reports/security_review_report.md
- docs/api/resource_allocation_api.md
- docs/api/vector_db_api.md
- docs/architecture/health_monitoring_protocol.md
- docs/ui/interactive_elements_guidelines.md
- docs/ui/navigator_customization.md
- docs/architecture/analytics_integration.md
- docs/development/day30_plan.md
- docs/user_guides/admin_user_mgmt.md
- docs/development/day25_plan.md
- docs/development/day20_plan.md
- docs/development/day29_plan.md
- docs/development/day17_plan.md
- docs/architecture/health_monitoring.md
- docs/development/tdd_docs_awareness_protocol.md
- docs/user_guides/external_integration.md
- docs/development/change_simulation_process.md
- docs/user_guides/week2_features.md
- docs/api/interventions_api.md
- docs/README.md
- docs/architecture/content_type_registry.md
- docs/development/day18_changelog.md
- docs/user_guides/conversation_usage.md
- docs/development/user_management_plan.md
- docs/development/test_coverage_notes_day18.md
- docs/api/feedback_format_specifications.md
- docs/architecture/dependency_tracking_protocol.md
- docs/api/manual_grading_procedures.md
- docs/api/metadata_schema_and_extension_points.md
- docs/development/day26_plan.md
- docs/ui/note_taking_features.md
- docs/api/service_health_protocol.md
- docs/user_guides/admin_workflows.md
- docs/reports/week2_progress_report.md
- docs/api/search_api.md
- docs/architecture/architecture_overview.md
- docs/development/pytest-qt-pyqt6-fix.md
- docs/api/tagging_system.md
- docs/architecture/dependency_maps.md
- docs/user_guides/content_extraction.md
- docs/development/day27_plan.md
- docs/api/progress_metrics.md
- docs/architecture/compatibility_impact_analysis.md
- docs/api/batch_content_metadata_api.md
- docs/reports/test_coverage_report.md
- docs/development/day10_done_criteria.md
- docs/user_guides/admin_course_mgmt.md
- docs/architecture/knowledge_graph.md
- docs/api/batch_operations.md
- docs/development/day18_plan.md
- docs/development/student_course_navigator.md
- docs/architecture/conversation_architecture.md
- docs/ui/professor_upload_widget_user.md
- docs/development/day15_plan.md
- docs/generated/README.md
- docs/development/day19_plan.md
- docs/user_guides/enrollment_workflow.md
- docs/development/day23_plan.md
- docs/integration_framework.md
- docs/development/day14_plan.md
- docs/development/advanced_ai_integration_workflows.md
- docs/api/grading_rule_specifications.md
- docs/development/day24_plan.md
- docs/development/day12_plan.md
- docs/user_guides/course_organization_features.md
- docs/api/assessment_delivery_workflow.md
- docs/development/tdd_workflow_guidelines.md
- docs/architecture/service_health_protocol.md
- docs/architecture/week2_integration.md
- docs/generated/index.md
- docs/api/feature_development_tracker.md
- docs/ui/student_dashboard_widget_api.md
- docs/user_guides/advanced_ai_integration_workflows.md
- docs/api/prompt_templates.md
- docs/content_management_integration.md
- docs/architecture/course_organization_integration.md
- docs/user_guides/concept_relationships.md
- docs/api/course_enrollment_api.md
- docs/architecture/vector_db.md
- docs/development/day16_plan.md
- docs/ui/multi_format_content_viewer.md
- docs/architecture/project_roadmap.md
- docs/api/notification_api.md
- docs/architecture/content_similarity.md
- docs/development/day11_done_criteria.md

### ⚠️ Unmatched in Index (Found in scan/output, not listed in doc_index.md):
- api/assessment_delivery_workflow.md
- api/batch_content_metadata_examples.md
- api/interventions_api.md
- architecture/health_monitoring_protocol.md
- api/manual_grading_procedures.md
- api/metadata_schema_and_extension_points.md
- api/batch_operations.md
- api/week2_api.md
- api/service_health_protocol.md
- api/student_dashboard_widgets.md
- api/search_api.md
- architecture/dependency_tracking_protocol.md
- api/milestone_tracker.md
- api/prompt_templates.md
- api/tagging_system.md
- api/progress_metrics.md
- api/grading_rule_specifications.md
- api/resource_allocation_api.md
- api/content_similarity_api.md
- api/batch_content_metadata_api.md
- api/resource_discovery_api.md
- api/upload_system_api.md
- api/course_enrollment_api.md
- api/feature_development_tracker.md
- api/feedback_format_specifications.md
- architecture/service_health_protocol.md
- api/user_management_api.md
- api/vector_db_api.md
- api/notification_api.md
- api/course_management_api.md

### Errors and Undocumented Sections:
- Undocumented: app/core/auth/credential_manager.py::CredentialManager
- Undocumented: app/core/auth/authentication.py::AdminAuthService
- Undocumented: app/core/auth/authentication.py::AdminRoles
- Undocumented: app/core/auth/authentication.py::AdminPermissions
- Undocumented: app/core/auth/authorization.py::PermissionError
- Undocumented: app/core/auth/permission_registry.py::assign_user_role
- Undocumented: app/core/auth/permission_registry.py::assign_user_permission
- Undocumented: app/core/auth/permission_registry.py::get_user_permissions
- Undocumented: app/core/db/db_client.py::DBClient
- Undocumented: app/core/db/event_hooks.py::EventBus
- Undocumented: app/core/db/event_hooks.py::after_insert
- Undocumented: app/core/db/event_hooks.py::after_update
- Undocumented: app/core/db/event_hooks.py::after_delete
- Undocumented: app/core/db/event_hooks.py::install_event_hooks
- Undocumented: app/core/db/content_db.py::ContentDB
- Undocumented: app/core/db/course_admin.py::CourseAdminService
- Undocumented: app/core/db/course_admin.py::CourseAdminService
- Undocumented: app/core/drive/file_operations.py::FileOperations
- Undocumented: app/core/drive/folder_structure.py::FolderStructure
- Undocumented: app/core/drive/metadata.py::MetadataManager
- Undocumented: app/core/drive/sync_manager.py::ConflictType
- Undocumented: app/core/drive/sync_manager.py::SyncConflict
- Undocumented: app/core/drive/sync_manager.py::SyncManager
- Undocumented: app/core/drive/metadata_schema_video.py::MetadataField
- Undocumented: app/core/drive/metadata_schema_video.py::MetadataSchema
- Undocumented: app/core/drive/metadata_inheritance_utilities.py::batch_apply_metadata
- Undocumented: app/core/ai/conversation.py::default_user_validator
- Undocumented: app/core/ai/conversation.py::default_handler
- Undocumented: app/core/api/api_client.py::DeepSeekAPIError
- Undocumented: app/core/api/api_client.py::GoogleDriveAPIError
- Undocumented: app/core/api/deepseek_client.py::DeepSeekAPIError
- Undocumented: app/core/api/google_drive_client.py::GoogleDriveAPIError
- Undocumented: app/core/upload/upload_service.py::UploadStatus
- Undocumented: app/core/upload/upload_service.py::UploadRequest
- Undocumented: app/core/upload/upload_service.py::UploadService
- Undocumented: app/core/validation/format_validator.py::ValidationResult
- Undocumented: app/core/validation/format_validator.py::BaseValidator
- Undocumented: app/core/validation/format_validator.py::PDFValidator
- Undocumented: app/core/validation/format_validator.py::ImageValidator
- Undocumented: app/core/validation/format_validator.py::VideoValidator
- Undocumented: app/core/validation/format_validator.py::TextValidator
- Undocumented: app/core/validation/format_validator.py::ValidationFramework
- Undocumented: app/core/validation/main.py::ValidationSystem
- Undocumented: app/core/monitoring/settings_manager.py::SettingValidationError
- Undocumented: app/core/monitoring/settings_manager.py::SystemSettingsManager
- Undocumented: app/core/monitoring/metrics.py::MetricType
- Undocumented: app/core/monitoring/metrics.py::AlertLevel
- Undocumented: app/core/monitoring/metrics.py::Metric
- Undocumented: app/core/monitoring/metrics.py::MetricAlert
- Undocumented: app/core/monitoring/metrics.py::SystemMetricsManager
- Undocumented: app/core/monitoring/notification_center.py::NotificationCategory
- Undocumented: app/core/monitoring/notification_center.py::NotificationPriority
- Undocumented: app/core/monitoring/notification_center.py::NotificationStatus
- Undocumented: app/core/monitoring/notification_center.py::Notification
- Undocumented: app/core/monitoring/integration_monitor.py::IntegrationHealthEvent
- Undocumented: app/core/monitoring/integration_monitor.py::IntegrationPointRegistry
- Undocumented: app/core/monitoring/resource_registry.py::ResourceAssignment
- Undocumented: app/core/monitoring/resource_registry.py::Resource
- Undocumented: app/core/extraction/structured_data_extractor.py::StructuredDataExtractionError
- Undocumented: app/core/extraction/text_extractor.py::TextExtractionError
- Undocumented: app/core/extraction/multimedia_metadata_extractor.py::MultimediaMetadataExtractionError
- Undocumented: app/core/vector_db/vector_db_client.py::VectorDBClient
- Undocumented: app/core/vector_db/schema.py::VectorEntry
- Undocumented: app/core/vector_db/schema.py::VectorDBIndexConfig
- Undocumented: app/core/vector_db/index_manager.py::VectorIndexManager
- Undocumented: app/core/vector_db/sync_manager.py::VectorDBSyncManager
- Undocumented: app/core/search/semantic_backend.py::cosine_similarity
- Undocumented: app/core/external_resources/__init__.py::ExternalResourceManager
- Undocumented: app/core/external_resources/providers.py::DeepSeekResourceProvider
- Undocumented: app/core/conversation/handlers.py::professor_content_handler
- Undocumented: app/core/conversation/handlers.py::admin_handler
- Undocumented: app/core/conversation/handlers.py::student_query_handler
- Undocumented: app/core/prompts/template_engine.py::TemplateNotFoundError
- Undocumented: app/core/prompts/parser.py::ResponseParser
- Undocumented: app/core/assessment/session_manager.py::AssessmentSessionStatus
- Undocumented: app/core/assessment/session_manager.py::AssessmentSession
- Undocumented: app/core/assessment/session_manager.py::AssessmentSessionManager
- Undocumented: app/core/assessment/question_engine.py::QuestionRenderError
- Undocumented: app/core/assessment/question_engine.py::QuestionEngine
- Undocumented: app/core/assessment/grading.py::GradingRuleError
- Undocumented: app/core/assessment/manual_grading.py::ManualGradingInterface
- Undocumented: app/core/assessment/feedback.py::FeedbackEngine
- Undocumented: app/core/project_management/milestone_tracker.py::MilestoneStatus
- Undocumented: app/core/project_management/milestone_tracker.py::MilestoneHistoryRecord
- Undocumented: app/core/project_management/milestone_tracker.py::Milestone
- Undocumented: app/core/project_management/feature_tracker.py::FeatureStatus
- Undocumented: app/core/project_management/feature_tracker.py::Feature
- Undocumented: app/core/project_management/feature_tracker.py::FeatureRegistry
- Undocumented: app/core/project_management/change_modeler.py::Change
- Undocumented: app/core/project_management/change_modeler.py::ChangeModeler
- Undocumented: app/core/project_management/change_propagation_analyzer.py::ChangePropagationAnalyzer
- Undocumented: app/core/project_management/change_effect_visualizer.py::ChangeEffectVisualizer
- Undocumented: app/core/project_management/migration_planner.py::MigrationPlanner
- Undocumented: integrations/registry/component_state.py::ComponentState
- Undocumented: integrations/monitoring/component_status_adapter.py::ComponentState
