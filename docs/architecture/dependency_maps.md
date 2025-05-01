flowchart TD
    ContentDB[/app/core/db/content_db.py/]
    ContentModel[/app/models/content.py/]
    StorageInterface[/integrations/interfaces/storage_interface.py/]
    AIInterface[/integrations/interfaces/ai_interface.py/]
    Orchestrator[/integrations/week2/orchestrator.py/]
    Coordinator[/app/core/integration/integration_coordinator.py/]
    SimilarityEngine[/app/core/ai/content_similarity.py/]
    AdminUI[/app/ui/admin/system_config.py/]
    HealthMonitor[/integrations/monitoring/integration_health.py/]

    ContentModel --> ContentDB
    ContentDB --> Orchestrator
    Orchestrator --> StorageInterface
    Orchestrator --> AIInterface
    Orchestrator --> SimilarityEngine
    Orchestrator --> AdminUI
    Orchestrator --> HealthMonitor
    Coordinator --> Orchestrator
    AdminUI --> HealthMonitor
    SimilarityEngine --> AdminUI