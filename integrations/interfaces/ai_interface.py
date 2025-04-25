"""
AI interface contracts for the AeroLearn AI system.

This module defines the interfaces for AI-powered components, including language models,
content analysis, question answering, and recommendation systems.
"""
import abc
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union, Tuple, AsyncIterator

from .base_interface import BaseInterface, InterfaceImplementation, InterfaceMethod
from .content_interface import ContentReference


class AIModelType(Enum):
    """Types of AI models used in the system."""
    LANGUAGE_MODEL = "language_model"
    EMBEDDING_MODEL = "embedding_model"
    CLASSIFICATION_MODEL = "classification_model"
    SUMMARIZATION_MODEL = "summarization_model"
    QUESTION_ANSWERING_MODEL = "question_answering_model"
    RECOMMENDATION_MODEL = "recommendation_model"
    CUSTOM_MODEL = "custom_model"


class AIModelCapability(Enum):
    """Specific capabilities that AI models might provide."""
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_SUMMARIZATION = "text_summarization"
    QUESTION_ANSWERING = "question_answering"
    CONTENT_RECOMMENDATION = "content_recommendation"
    CONTENT_SIMILARITY = "content_similarity"
    TOPIC_EXTRACTION = "topic_extraction"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    CONCEPTUAL_MAPPING = "conceptual_mapping"


class AIProviderType(Enum):
    """Types of AI providers."""
    LOCAL = "local"             # AI models running locally
    DEEPSEEK = "deepseek"       # DeepSeek AI models
    OPENAI = "openai"           # OpenAI models
    HUGGINGFACE = "huggingface" # HuggingFace models
    ANTHROPIC = "anthropic"     # Anthropic models
    CUSTOM = "custom"           # Custom AI provider


class AIModelMetadata:
    """Metadata about an AI model."""
    
    def __init__(self,
                 model_id: str,
                 model_name: str,
                 model_type: AIModelType,
                 provider: AIProviderType,
                 capabilities: List[AIModelCapability],
                 version: str = None,
                 context_length: int = None,
                 input_cost_per_1k: float = None,
                 output_cost_per_1k: float = None,
                 requires_api_key: bool = False,
                 documentation_url: str = None,
                 additional_info: Dict[str, Any] = None):
        """
        Initialize AI model metadata.
        
        Args:
            model_id: Unique identifier for the model
            model_name: Display name for the model
            model_type: Type of the model
            provider: Provider of the model
            capabilities: List of model capabilities
            version: Version of the model
            context_length: Maximum context length in tokens
            input_cost_per_1k: Cost per 1,000 input tokens
            output_cost_per_1k: Cost per 1,000 output tokens
            requires_api_key: Whether the model requires an API key
            documentation_url: URL to model documentation
            additional_info: Additional model information
        """
        self.model_id = model_id
        self.model_name = model_name
        self.model_type = model_type
        self.provider = provider
        self.capabilities = capabilities
        self.version = version
        self.context_length = context_length
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k
        self.requires_api_key = requires_api_key
        self.documentation_url = documentation_url
        self.additional_info = additional_info or {}


class AIRequest:
    """Base class for AI requests."""
    
    def __init__(self,
                 model_id: str,
                 user_id: str = None,
                 request_id: str = None,
                 max_tokens: int = None,
                 temperature: float = None,
                 options: Dict[str, Any] = None):
        """
        Initialize an AI request.
        
        Args:
            model_id: ID of the model to use
            user_id: ID of the user making the request
            request_id: Unique identifier for the request (generated if None)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling (higher is more random)
            options: Additional model-specific options
        """
        self.model_id = model_id
        self.user_id = user_id
        self.request_id = request_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.options = options or {}


class TextGenerationRequest(AIRequest):
    """Request for text generation."""
    
    def __init__(self,
                 model_id: str,
                 prompt: str,
                 system_message: str = None,
                 chat_history: List[Dict[str, str]] = None,
                 **kwargs):
        """
        Initialize a text generation request.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt text
            system_message: System message for chat completions
            chat_history: Previous messages in the conversation
            **kwargs: Additional parameters passed to AIRequest
        """
        super().__init__(model_id=model_id, **kwargs)
        self.prompt = prompt
        self.system_message = system_message
        self.chat_history = chat_history or []


class EmbeddingRequest(AIRequest):
    """Request for text embedding."""
    
    def __init__(self,
                 model_id: str,
                 texts: List[str],
                 **kwargs):
        """
        Initialize an embedding request.
        
        Args:
            model_id: ID of the model to use
            texts: List of texts to embed
            **kwargs: Additional parameters passed to AIRequest
        """
        super().__init__(model_id=model_id, **kwargs)
        self.texts = texts


class AIResponse:
    """Base class for AI responses."""
    
    def __init__(self,
                 request_id: str,
                 model_id: str,
                 usage: Dict[str, int] = None,
                 elapsed_time: float = None,
                 status: str = "success",
                 error_message: str = None):
        """
        Initialize an AI response.
        
        Args:
            request_id: ID of the request this is a response to
            model_id: ID of the model that generated the response
            usage: Usage statistics (e.g., prompt_tokens, completion_tokens)
            elapsed_time: Time taken to generate the response in seconds
            status: Status of the response ("success", "error", etc.)
            error_message: Error message if status is "error"
        """
        self.request_id = request_id
        self.model_id = model_id
        self.usage = usage or {}
        self.elapsed_time = elapsed_time
        self.status = status
        self.error_message = error_message


class TextGenerationResponse(AIResponse):
    """Response from text generation."""
    
    def __init__(self,
                 request_id: str,
                 model_id: str,
                 text: str,
                 finish_reason: str = None,
                 **kwargs):
        """
        Initialize a text generation response.
        
        Args:
            request_id: ID of the request this is a response to
            model_id: ID of the model that generated the response
            text: Generated text
            finish_reason: Reason why generation stopped
            **kwargs: Additional parameters passed to AIResponse
        """
        super().__init__(request_id=request_id, model_id=model_id, **kwargs)
        self.text = text
        self.finish_reason = finish_reason


class EmbeddingResponse(AIResponse):
    """Response from text embedding."""
    
    def __init__(self,
                 request_id: str,
                 model_id: str,
                 embeddings: List[List[float]],
                 **kwargs):
        """
        Initialize an embedding response.
        
        Args:
            request_id: ID of the request this is a response to
            model_id: ID of the model that generated the response
            embeddings: List of embedding vectors
            **kwargs: Additional parameters passed to AIResponse
        """
        super().__init__(request_id=request_id, model_id=model_id, **kwargs)
        self.embeddings = embeddings


class AIModelProviderInterface(BaseInterface):
    """
    Interface for components that provide access to AI models.
    """
    interface_name = "ai_model_provider"
    interface_version = "1.0.0"
    interface_description = "Interface for components that provide access to AI models"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def list_models(self) -> List[AIModelMetadata]:
        """
        List available AI models.
        
        Returns:
            List of available model metadata
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_model_metadata(self, model_id: str) -> Optional[AIModelMetadata]:
        """
        Get metadata for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model metadata if found, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def text_generation(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        Generate text from a prompt.
        
        Args:
            request: Text generation request
            
        Returns:
            Text generation response
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def stream_text_generation(self, request: TextGenerationRequest) -> AsyncIterator[str]:
        """
        Stream generated text as it's produced.
        
        Args:
            request: Text generation request
            
        Returns:
            Async iterator yielding generated text chunks
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Get embeddings for text.
        
        Args:
            request: Embedding request
            
        Returns:
            Embedding response
        """
        pass


class ContentAnalysisInterface(BaseInterface):
    """
    Interface for AI components that analyze educational content.
    """
    interface_name = "content_analysis"
    interface_version = "1.0.0"
    interface_description = "Interface for AI components that analyze educational content"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def extract_key_concepts(self, content_reference: ContentReference) -> List[Dict[str, Any]]:
        """
        Extract key concepts from content.
        
        Args:
            content_reference: Reference to the content to analyze
            
        Returns:
            List of concepts with relevance scores and context
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def analyze_difficulty(self, content_reference: ContentReference) -> Dict[str, Any]:
        """
        Analyze the difficulty level of content.
        
        Args:
            content_reference: Reference to the content to analyze
            
        Returns:
            Difficulty analysis results
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def generate_quiz_questions(self, content_reference: ContentReference, 
                                     count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """
        Generate quiz questions based on content.
        
        Args:
            content_reference: Reference to the content
            count: Number of questions to generate
            difficulty: Difficulty level of questions
            
        Returns:
            List of generated questions with answers
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def suggest_improvements(self, content_reference: ContentReference) -> List[Dict[str, Any]]:
        """
        Suggest improvements for content.
        
        Args:
            content_reference: Reference to the content
            
        Returns:
            List of improvement suggestions
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def find_related_content(self, content_reference: ContentReference, 
                                  max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find content related to the specified content.
        
        Args:
            content_reference: Reference to the content
            max_results: Maximum number of results to return
            
        Returns:
            List of related content with similarity scores
        """
        pass


class LearningAssistantInterface(BaseInterface):
    """
    Interface for AI components that provide learning assistance.
    """
    interface_name = "learning_assistant"
    interface_version = "1.0.0"
    interface_description = "Interface for AI components that provide learning assistance"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def answer_question(self, question: str, context_references: List[ContentReference] = None, 
                            user_id: str = None) -> Dict[str, Any]:
        """
        Answer a student's question with relevant content.
        
        Args:
            question: The question to answer
            context_references: Optional context content references
            user_id: ID of the user asking the question
            
        Returns:
            Answer with sources and confidence
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def explain_concept(self, concept: str, detail_level: str = "medium", 
                            user_id: str = None) -> Dict[str, Any]:
        """
        Explain an aerospace engineering concept.
        
        Args:
            concept: The concept to explain
            detail_level: Level of detail in the explanation
            user_id: ID of the user requesting the explanation
            
        Returns:
            Explanation with diagrams and references
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def generate_study_plan(self, topics: List[str], time_available: int, 
                                prior_knowledge: str = "beginner", user_id: str = None) -> Dict[str, Any]:
        """
        Generate a personalized study plan.
        
        Args:
            topics: List of topics to study
            time_available: Available time in minutes
            prior_knowledge: Prior knowledge level
            user_id: ID of the user
            
        Returns:
            Structured study plan
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def provide_feedback(self, student_work: str, assignment_reference: ContentReference = None, 
                              rubric_reference: ContentReference = None, user_id: str = None) -> Dict[str, Any]:
        """
        Provide feedback on student work.
        
        Args:
            student_work: The student's work to evaluate
            assignment_reference: Reference to the assignment
            rubric_reference: Reference to the grading rubric
            user_id: ID of the student
            
        Returns:
            Detailed feedback with suggestions
        """
        pass


class PersonalizationInterface(BaseInterface):
    """
    Interface for AI components that provide personalized recommendations.
    """
    interface_name = "personalization"
    interface_version = "1.0.0"
    interface_description = "Interface for AI components that provide personalized recommendations"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def recommend_content(self, user_id: str, count: int = 5) -> List[ContentReference]:
        """
        Recommend content for a user based on their profile and history.
        
        Args:
            user_id: ID of the user
            count: Number of recommendations to generate
            
        Returns:
            List of recommended content references
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def identify_knowledge_gaps(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Identify knowledge gaps for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of identified knowledge gaps with confidence scores
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def recommend_learning_path(self, user_id: str, goal: str) -> Dict[str, Any]:
        """
        Recommend a learning path to achieve a specific goal.
        
        Args:
            user_id: ID of the user
            goal: Learning goal
            
        Returns:
            Structured learning path recommendation
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's learning profile based on their activity.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User learning profile with preferences, strengths, and weaknesses
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a user's learning profile with new information.
        
        Args:
            user_id: ID of the user
            updates: Profile updates to apply
            
        Returns:
            True if profile updated successfully, False otherwise
        """
        pass


class AIUsageTrackingInterface(BaseInterface):
    """
    Interface for components that track AI usage and costs.
    """
    interface_name = "ai_usage_tracking"
    interface_version = "1.0.0"
    interface_description = "Interface for components that track AI usage and costs"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def record_usage(self, model_id: str, tokens_input: int, tokens_output: int, 
                         user_id: str = None, purpose: str = None) -> bool:
        """
        Record AI model usage.
        
        Args:
            model_id: ID of the model used
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            user_id: ID of the user (if applicable)
            purpose: Purpose of the usage
            
        Returns:
            True if usage recorded successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_usage_stats(self, timeframe: str = "day", user_id: str = None) -> Dict[str, Any]:
        """
        Get AI usage statistics.
        
        Args:
            timeframe: Time period to get stats for ("day", "week", "month")
            user_id: Optional user ID to filter stats by
            
        Returns:
            Usage statistics for the specified timeframe
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_cost_estimate(self, timeframe: str = "month") -> Dict[str, float]:
        """
        Get estimated costs for AI usage.
        
        Args:
            timeframe: Time period to get costs for ("day", "week", "month")
            
        Returns:
            Cost estimates broken down by model and purpose
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def set_usage_limits(self, limits: Dict[str, Any]) -> bool:
        """
        Set usage limits for AI services.
        
        Args:
            limits: Dictionary of limit settings
            
        Returns:
            True if limits set successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def check_usage_limit(self, model_id: str, tokens: int, user_id: str = None) -> bool:
        """
        Check if a usage request is within limits.
        
        Args:
            model_id: ID of the model to use
            tokens: Estimated number of tokens for the request
            user_id: Optional user ID to check limits for
            
        Returns:
            True if within limits, False if would exceed limits
        """
        pass


import asyncio

# Register all interfaces defined in this module
def register_ai_interfaces() -> None:
    """
    Register all AI interfaces.
    
    This function should be called during system initialization.
    """
    event_bus = EventBus()
    
    for interface_cls in [AIModelProviderInterface, ContentAnalysisInterface, 
                         LearningAssistantInterface, PersonalizationInterface,
                         AIUsageTrackingInterface]:
        try:
            interface_cls.register_interface()
            
            # Publish event for monitoring
            from ..events.event_types import Event, EventCategory, EventPriority
            event = Event(
                event_type="interface.registered",
                category=EventCategory.SYSTEM,
                source_component="ai_interfaces",
                priority=EventPriority.NORMAL,
                data={
                    "interface_name": interface_cls.interface_name,
                    "version": interface_cls.interface_version,
                    "description": interface_cls.interface_description
                },
                is_persistent=True
            )
            asyncio.create_task(event_bus.publish(event))
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"Error registering AI interface {interface_cls.__name__}: {str(e)}"
            )
