"""
Transaction logging for the AeroLearn AI system.

This module provides tools for tracking and logging cross-component transactions,
making it easier to trace operations as they flow through different parts of the system.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple, Callable, Union
import uuid
import threading
import time
import json
from contextlib import contextmanager

from integrations.events.event_types import Event, EventCategory, EventPriority
from integrations.registry.component_registry import Component


class TransactionStage(Enum):
    """Stages of a transaction lifecycle."""
    CREATED = auto()    # Transaction has been created
    STARTED = auto()    # Transaction processing has started
    PROCESSING = auto() # Transaction is being processed
    COMPLETED = auto()  # Transaction completed successfully
    FAILED = auto()     # Transaction failed
    CANCELED = auto()   # Transaction was canceled


class TransactionEvent(Event):
    """Event fired when a transaction changes stage."""
    
    def __init__(
        self,
        transaction_id: str,
        stage: TransactionStage,
        component_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a transaction event.
        
        Args:
            transaction_id: ID of the transaction
            stage: Current stage of the transaction
            component_id: ID of the component that generated the event
            metadata: Additional data related to the transaction
        """
        super().__init__()
        self.transaction_id = transaction_id
        self.stage = stage
        self.component_id = component_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.category = EventCategory.SYSTEM
        
        # Higher priority for failed transactions
        self.priority = (
            EventPriority.HIGH if stage == TransactionStage.FAILED
            else EventPriority.MEDIUM
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'transaction_id': self.transaction_id,
            'stage': self.stage.name,
            'component_id': self.component_id,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.name,
            'priority': self.priority.name
        }


class TransactionError(Exception):
    """Exception raised for errors in transaction processing."""
    pass


class Transaction:
    """
    Represents a cross-component transaction.
    
    A transaction is a logical unit of work that may involve multiple
    components. This class tracks the flow of a transaction through
    the system and provides status tracking and timing information.
    """
    
    def __init__(
        self,
        transaction_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new transaction.
        
        Args:
            transaction_id: Unique ID for the transaction (generated if None)
            parent_id: ID of parent transaction (for nested transactions)
            name: Human-readable name for the transaction
            metadata: Additional data related to the transaction
        """
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.parent_id = parent_id
        self.name = name or f"Transaction-{self.transaction_id[:8]}"
        self.metadata = metadata or {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.stage = TransactionStage.CREATED
        self.components: List[str] = []  # Components involved in this transaction
        self.stages: List[Dict[str, Any]] = []  # Stage history
        self.tags: Set[str] = set()  # Tags for filtering/categorizing transactions
        self.errors: List[Dict[str, str]] = []  # Errors encountered during transaction
        
        # Add initial stage
        self._add_stage(TransactionStage.CREATED, None)
    
    def start(self, component_id: Optional[str] = None) -> Transaction:
        """
        Start the transaction.
        
        Args:
            component_id: ID of the component starting the transaction
            
        Returns:
            Self for method chaining
        """
        self.start_time = time.time()
        self.stage = TransactionStage.STARTED
        self._add_stage(TransactionStage.STARTED, component_id)
        return self
    
    def process(self, component_id: str, action: str = "") -> Transaction:
        """
        Update transaction to processing stage.
        
        Args:
            component_id: ID of the component processing the transaction
            action: Description of the processing action
            
        Returns:
            Self for method chaining
        """
        self.stage = TransactionStage.PROCESSING
        self._add_stage(
            TransactionStage.PROCESSING,
            component_id,
            metadata={'action': action} if action else None
        )
        return self
    
    def complete(self, component_id: Optional[str] = None, result: Any = None) -> Transaction:
        """
        Mark the transaction as complete.
        
        Args:
            component_id: ID of the component completing the transaction
            result: Final result of the transaction
            
        Returns:
            Self for method chaining
        """
        self.end_time = time.time()
        self.stage = TransactionStage.COMPLETED
        self._add_stage(
            TransactionStage.COMPLETED,
            component_id,
            metadata={'result': str(result)} if result is not None else None
        )
        return self
    
    def fail(self, component_id: str, error: Union[str, Exception]) -> Transaction:
        """
        Mark the transaction as failed.
        
        Args:
            component_id: ID of the component where the failure occurred
            error: Error message or exception
            
        Returns:
            Self for method chaining
        """
        self.end_time = time.time()
        self.stage = TransactionStage.FAILED
        
        # Store error details
        error_dict = {
            'component_id': component_id,
            'timestamp': datetime.now().isoformat(),
        }
        
        if isinstance(error, Exception):
            error_dict['message'] = str(error)
            error_dict['type'] = type(error).__name__
        else:
            error_dict['message'] = error
            error_dict['type'] = 'Error'
            
        self.errors.append(error_dict)
        
        self._add_stage(
            TransactionStage.FAILED,
            component_id,
            metadata={'error': error_dict['message'], 'error_type': error_dict['type']}
        )
        return self
    
    def cancel(self, component_id: Optional[str] = None, reason: str = "") -> Transaction:
        """
        Mark the transaction as canceled.
        
        Args:
            component_id: ID of the component canceling the transaction
            reason: Reason for cancelation
            
        Returns:
            Self for method chaining
        """
        self.end_time = time.time()
        self.stage = TransactionStage.CANCELED
        self._add_stage(
            TransactionStage.CANCELED,
            component_id,
            metadata={'reason': reason} if reason else None
        )
        return self
    
    def add_tag(self, tag: str) -> Transaction:
        """
        Add a tag to the transaction.
        
        Args:
            tag: Tag to add
            
        Returns:
            Self for method chaining
        """
        self.tags.add(tag)
        return self
    
    def add_metadata(self, key: str, value: Any) -> Transaction:
        """
        Add metadata to the transaction.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            Self for method chaining
        """
        self.metadata[key] = value
        return self
    
    def duration(self) -> Optional[float]:
        """
        Get the transaction duration in seconds.
        
        Returns:
            Duration in seconds or None if transaction hasn't ended
        """
        if self.start_time is None:
            return None
            
        end = self.end_time or time.time()
        return end - self.start_time
    
    def _add_stage(
        self,
        stage: TransactionStage,
        component_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a stage to the transaction history.
        
        Args:
            stage: Transaction stage
            component_id: ID of the component
            metadata: Additional stage metadata
        """
        stage_entry = {
            'stage': stage.name,
            'timestamp': datetime.now().isoformat(),
            'time': time.time()
        }
        
        if component_id:
            stage_entry['component_id'] = component_id
            if component_id not in self.components:
                self.components.append(component_id)
                
        if metadata:
            stage_entry['metadata'] = metadata
            
        self.stages.append(stage_entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'transaction_id': self.transaction_id,
            'name': self.name,
            'stage': self.stage.name,
            'components': self.components,
            'tags': list(self.tags),
            'stages': self.stages,
            'metadata': self.metadata,
            'errors': self.errors
        }
        
        if self.parent_id:
            result['parent_id'] = self.parent_id
            
        if self.start_time:
            result['start_time'] = self.start_time
            result['start_time_iso'] = datetime.fromtimestamp(self.start_time).isoformat()
            
        if self.end_time:
            result['end_time'] = self.end_time
            result['end_time_iso'] = datetime.fromtimestamp(self.end_time).isoformat()
            result['duration'] = self.end_time - self.start_time
            
        return result


class TransactionContext:
    """
    Context manager for transaction handling.
    
    Makes it easy to use transactions in with statements, handling
    start, completion, and error conditions automatically.
    """
    
    def __init__(
        self,
        transaction: Transaction,
        component_id: str,
        action: str = "",
        logger: Optional[TransactionLogger] = None
    ):
        """
        Initialize a transaction context.
        
        Args:
            transaction: Transaction to manage
            component_id: ID of the component using this transaction
            action: Description of the action being performed
            logger: TransactionLogger instance (if None, transaction won't be logged)
        """
        self.transaction = transaction
        self.component_id = component_id
        self.action = action
        self.logger = logger
        self._transaction_started = False
    
    def __enter__(self) -> Transaction:
        """Start the transaction and return it."""
        if self.transaction.stage == TransactionStage.CREATED:
            self.transaction.start(self.component_id)
            self._transaction_started = True
        
        self.transaction.process(self.component_id, self.action)
        
        if self.logger:
            self.logger.update_transaction(self.transaction)
            
        return self.transaction
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Complete or fail the transaction based on exception state.
        
        Args:
            exc_type: Exception type if an exception was raised, otherwise None
            exc_val: Exception value if an exception was raised, otherwise None
            exc_tb: Exception traceback if an exception was raised, otherwise None
            
        Returns:
            False to propagate exceptions, True to suppress
        """
        if exc_type is not None:
            # An exception occurred, mark transaction as failed
            self.transaction.fail(self.component_id, exc_val)
        else:
            # No exception, mark transaction as completed
            self.transaction.complete(self.component_id)
            
        if self.logger:
            self.logger.update_transaction(self.transaction)
            
        # Don't suppress the exception
        return False


class TransactionLogger(Component):
    """
    System for logging and tracking cross-component transactions.
    
    This class maintains an in-memory record of recent transactions and
    provides utilities for creating, updating, and retrieving transaction
    information. It can also persist transactions to external storage.
    """
    
    def __init__(
        self,
        max_transactions: int = 1000,
        auto_prune: bool = True,
        persistent_storage: bool = False
    ):
        """
        Initialize the transaction logger.
        
        Args:
            max_transactions: Maximum number of transactions to keep in memory
            auto_prune: Whether to automatically prune old transactions
            persistent_storage: Whether to persist transactions to storage
        """
        super().__init__(
            component_id="system.transaction_logger",
            component_type="monitoring",
            version="1.0.0"
        )
        self.name = "Transaction Logger"
        self.max_transactions = max_transactions
        self.auto_prune = auto_prune
        self.persistent_storage = persistent_storage
        self.transactions: Dict[str, Transaction] = {}
        self.transactions_by_parent: Dict[str, List[str]] = {}
        self.transactions_by_component: Dict[str, List[str]] = {}
        self.transactions_by_tag: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        self._next_id = 0
    
    def create_transaction(
        self,
        name: str = "",
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            name: Human-readable name for the transaction
            parent_id: ID of parent transaction (for nested transactions)
            metadata: Additional data related to the transaction
            tags: Tags for filtering/categorizing the transaction
            
        Returns:
            Newly created transaction
        """
        with self._lock:
            # Generate a sequential transaction ID
            self._next_id += 1
            transaction_id = f"tx-{int(time.time())}-{self._next_id}"
            
            # Create the transaction
            transaction = Transaction(
                transaction_id=transaction_id,
                parent_id=parent_id,
                name=name or f"Transaction-{self._next_id}",
                metadata=metadata
            )
            
            # Add tags
            if tags:
                for tag in tags:
                    transaction.add_tag(tag)
                    
            # Store the transaction
            self._store_transaction(transaction)
                    
            return transaction
    
    def update_transaction(self, transaction: Transaction) -> None:
        """
        Update a transaction in the log.
        
        Args:
            transaction: Transaction to update
        """
        with self._lock:
            self._store_transaction(transaction)
            
            # Generate and publish event if stage changed
            # Would integrate with EventBus in a real implementation
            event = TransactionEvent(
                transaction_id=transaction.transaction_id,
                stage=transaction.stage,
                component_id=transaction.components[-1] if transaction.components else "unknown",
                metadata={
                    'name': transaction.name,
                    'duration': transaction.duration()
                }
            )
            
            # In a real implementation, we would do:
            # from integrations.events.event_bus import EventBus
            # EventBus().publish(event)
            
            # Just print for testing
            print(f"Transaction {transaction.name} ({transaction.transaction_id}) is now {transaction.stage.name}")
            
            # Persist if needed
            if self.persistent_storage and transaction.stage in (
                TransactionStage.COMPLETED, TransactionStage.FAILED, TransactionStage.CANCELED
            ):
                self._persist_transaction(transaction)
            
            # Prune if needed
            if self.auto_prune and len(self.transactions) > self.max_transactions:
                self._prune_transactions()
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: ID of the transaction
            
        Returns:
            Transaction or None if not found
        """
        with self._lock:
            return self.transactions.get(transaction_id)
    
    def get_transactions_by_parent(self, parent_id: str) -> List[Transaction]:
        """
        Get child transactions of a parent transaction.
        
        Args:
            parent_id: ID of the parent transaction
            
        Returns:
            List of child transactions
        """
        with self._lock:
            if parent_id not in self.transactions_by_parent:
                return []
                
            return [
                self.transactions[tx_id]
                for tx_id in self.transactions_by_parent[parent_id]
                if tx_id in self.transactions
            ]
    
    def get_transactions_by_component(self, component_id: str) -> List[Transaction]:
        """
        Get transactions involving a specific component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of transactions
        """
        with self._lock:
            if component_id not in self.transactions_by_component:
                return []
                
            return [
                self.transactions[tx_id]
                for tx_id in self.transactions_by_component[component_id]
                if tx_id in self.transactions
            ]
    
    def get_transactions_by_tag(self, tag: str) -> List[Transaction]:
        """
        Get transactions with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of transactions
        """
        with self._lock:
            if tag not in self.transactions_by_tag:
                return []
                
            return [
                self.transactions[tx_id]
                for tx_id in self.transactions_by_tag[tag]
                if tx_id in self.transactions
            ]
    
    def get_transactions_by_stage(self, stage: TransactionStage) -> List[Transaction]:
        """
        Get transactions in a specific stage.
        
        Args:
            stage: Stage to filter by
            
        Returns:
            List of transactions
        """
        with self._lock:
            return [
                tx for tx in self.transactions.values()
                if tx.stage == stage
            ]
    
    def get_active_transactions(self) -> List[Transaction]:
        """
        Get all active (non-completed) transactions.
        
        Returns:
            List of active transactions
        """
        with self._lock:
            return [
                tx for tx in self.transactions.values()
                if tx.stage not in (
                    TransactionStage.COMPLETED,
                    TransactionStage.FAILED,
                    TransactionStage.CANCELED
                )
            ]
    
    def transaction_context(
        self,
        component_id: str,
        name: str = "",
        action: str = "",
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> TransactionContext:
        """
        Create a transaction context for use in with statements.
        
        Args:
            component_id: ID of the component using this transaction
            name: Human-readable name for the transaction
            action: Description of the action being performed
            parent_id: ID of parent transaction (for nested transactions)
            metadata: Additional data related to the transaction
            tags: Tags for filtering/categorizing the transaction
            
        Returns:
            Transaction context manager
        """
        transaction = self.create_transaction(
            name=name, 
            parent_id=parent_id,
            metadata=metadata,
            tags=tags
        )
        
        return TransactionContext(
            transaction=transaction,
            component_id=component_id,
            action=action,
            logger=self
        )
    
    def clear_completed_transactions(self, max_age_seconds: Optional[float] = None) -> int:
        """
        Clear completed, failed, and canceled transactions.
        
        Args:
            max_age_seconds: Only clear transactions older than this many seconds
            
        Returns:
            Number of transactions cleared
        """
        with self._lock:
            to_remove = []
            current_time = time.time()
            
            for tx_id, tx in self.transactions.items():
                if tx.stage in (
                    TransactionStage.COMPLETED,
                    TransactionStage.FAILED,
                    TransactionStage.CANCELED
                ):
                    if max_age_seconds is None or (
                        tx.end_time is not None and 
                        current_time - tx.end_time > max_age_seconds
                    ):
                        to_remove.append(tx_id)
            
            for tx_id in to_remove:
                self._remove_transaction(tx_id)
                
            return len(to_remove)
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """
        Get a summary of transaction statistics.
        
        Returns:
            Dictionary with transaction summary information
        """
        with self._lock:
            # Count transactions by stage
            stage_counts = {stage.name: 0 for stage in TransactionStage}
            for tx in self.transactions.values():
                stage_counts[tx.stage.name] += 1
                
            # Get active transaction count by component
            active_by_component: Dict[str, int] = {}
            for tx in self.get_active_transactions():
                for component_id in tx.components:
                    active_by_component[component_id] = active_by_component.get(component_id, 0) + 1
            
            # Calculate average duration of completed transactions
            completed_durations = [
                tx.duration() for tx in self.transactions.values()
                if tx.stage == TransactionStage.COMPLETED and tx.duration() is not None
            ]
            
            avg_duration = (
                sum(completed_durations) / len(completed_durations)
                if completed_durations else None
            )
            
            # Calculate error rate
            total_finished = stage_counts[TransactionStage.COMPLETED.name] + \
                             stage_counts[TransactionStage.FAILED.name] + \
                             stage_counts[TransactionStage.CANCELED.name]
                             
            error_rate = (
                stage_counts[TransactionStage.FAILED.name] / total_finished
                if total_finished > 0 else 0
            )
            
            return {
                'total_transactions': len(self.transactions),
                'active_transactions': len(self.get_active_transactions()),
                'stage_counts': stage_counts,
                'active_by_component': active_by_component,
                'average_duration': avg_duration,
                'error_rate': error_rate,
                'timestamp': datetime.now().isoformat()
            }
    
    def _store_transaction(self, transaction: Transaction) -> None:
        """
        Store or update a transaction in internal indexes.
        
        Args:
            transaction: Transaction to store
        """
        tx_id = transaction.transaction_id
        
        # Store in main index
        self.transactions[tx_id] = transaction
        
        # Index by parent
        if transaction.parent_id:
            if transaction.parent_id not in self.transactions_by_parent:
                self.transactions_by_parent[transaction.parent_id] = []
            if tx_id not in self.transactions_by_parent[transaction.parent_id]:
                self.transactions_by_parent[transaction.parent_id].append(tx_id)
        
        # Index by component
        for component_id in transaction.components:
            if component_id not in self.transactions_by_component:
                self.transactions_by_component[component_id] = []
            if tx_id not in self.transactions_by_component[component_id]:
                self.transactions_by_component[component_id].append(tx_id)
        
        # Index by tag
        for tag in transaction.tags:
            if tag not in self.transactions_by_tag:
                self.transactions_by_tag[tag] = []
            if tx_id not in self.transactions_by_tag[tag]:
                self.transactions_by_tag[tag].append(tx_id)
    
    def _remove_transaction(self, transaction_id: str) -> None:
        """
        Remove a transaction from all indexes.
        
        Args:
            transaction_id: ID of transaction to remove
        """
        if transaction_id not in self.transactions:
            return
            
        # Get the transaction
        transaction = self.transactions[transaction_id]
        
        # Remove from main index
        del self.transactions[transaction_id]
        
        # Remove from parent index
        if transaction.parent_id and transaction.parent_id in self.transactions_by_parent:
            if transaction_id in self.transactions_by_parent[transaction.parent_id]:
                self.transactions_by_parent[transaction.parent_id].remove(transaction_id)
            if not self.transactions_by_parent[transaction.parent_id]:
                del self.transactions_by_parent[transaction.parent_id]
        
        # Remove from component index
        for component_id in transaction.components:
            if component_id in self.transactions_by_component:
                if transaction_id in self.transactions_by_component[component_id]:
                    self.transactions_by_component[component_id].remove(transaction_id)
                if not self.transactions_by_component[component_id]:
                    del self.transactions_by_component[component_id]
        
        # Remove from tag index
        for tag in transaction.tags:
            if tag in self.transactions_by_tag:
                if transaction_id in self.transactions_by_tag[tag]:
                    self.transactions_by_tag[tag].remove(transaction_id)
                if not self.transactions_by_tag[tag]:
                    del self.transactions_by_tag[tag]
    
    def _prune_transactions(self) -> None:
        """Prune old transactions to stay within max_transactions limit."""
        with self._lock:
            if len(self.transactions) <= self.max_transactions:
                return
                
            # Find oldest completed transactions to remove
            to_prune = []
            for tx_id, tx in self.transactions.items():
                if tx.stage in (
                    TransactionStage.COMPLETED,
                    TransactionStage.FAILED,
                    TransactionStage.CANCELED
                ):
                    to_prune.append((tx_id, tx.end_time or 0))
                    
            # Sort by end_time (oldest first)
            to_prune.sort(key=lambda x: x[1])
            
            # Remove oldest transactions until we're under the limit
            while len(self.transactions) > self.max_transactions and to_prune:
                tx_id, _ = to_prune.pop(0)
                self._remove_transaction(tx_id)
                
            # If we're still over limit, start removing active transactions
            # as a last resort
            if len(self.transactions) > self.max_transactions:
                to_prune = [
                    (tx_id, tx.start_time or 0)
                    for tx_id, tx in self.transactions.items()
                ]
                
                # Sort by start_time (oldest first)
                to_prune.sort(key=lambda x: x[1])
                
                # Remove oldest transactions until we're under the limit
                while len(self.transactions) > self.max_transactions and to_prune:
                    tx_id, _ = to_prune.pop(0)
                    self._remove_transaction(tx_id)
    
    def _persist_transaction(self, transaction: Transaction) -> None:
        """
        Persist a transaction to storage.
        
        In a real implementation, this would write to a database or log file.
        Here we'll just simulate persistence with a print statement.
        
        Args:
            transaction: Transaction to persist
        """
        if not self.persistent_storage:
            return
            
        # Convert to JSON for storage
        json_data = json.dumps(transaction.to_dict())
        
        # In a real implementation, would store to database or file
        # For now, just print
        print(f"Persisting transaction: {json_data[:100]}...")
    
    def log_transaction(self, source: str, target: str, type_: str, data: Any) -> None:
        """
        Log a simple transaction for testing purposes.
        
        Args:
            source: Source component or system
            target: Target component or system
            type_: Type of transaction
            data: Transaction data
        """
        if not hasattr(self, '_logs'):
            self._logs = []
            
        entry = {"source": source, "target": target, "type": type_, "data": data}
        self._logs.append(entry)
        
    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all simple transaction logs.
        
        Returns:
            List of transaction log entries
        """
        if not hasattr(self, '_logs'):
            self._logs = []
            
        return self._logs
    
    @contextmanager
    def start_transaction(
        self,
        component_id: str,
        name: str = "",
        action: str = "",
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Transaction:
        """
        Start a transaction and provide it as a context manager.
        
        Args:
            component_id: ID of the component starting the transaction
            name: Human-readable name for the transaction
            action: Description of the action being performed
            parent_id: ID of parent transaction (for nested transactions)
            metadata: Additional data related to the transaction
            tags: Tags for filtering/categorizing the transaction
            
        Yields:
            The started transaction
            
        Example:
            with transaction_logger.start_transaction(
                component_id='my.component',
                name='Important Operation'
            ) as tx:
                # Do work
                tx.add_metadata('key', 'value')
        """
        try:
            # Create and start the transaction
            transaction = self.create_transaction(
                name=name,
                parent_id=parent_id,
                metadata=metadata,
                tags=tags
            )
            transaction.start(component_id)
            transaction.process(component_id, action)
            self.update_transaction(transaction)
            
            # Yield the transaction to the caller
            yield transaction
            
            # If we get here normally, complete the transaction
            if transaction.stage not in (
                TransactionStage.COMPLETED,
                TransactionStage.FAILED,
                TransactionStage.CANCELED
            ):
                transaction.complete(component_id)
                self.update_transaction(transaction)
                
        except Exception as e:
            # If an exception occurred, mark the transaction as failed
            if transaction.stage not in (
                TransactionStage.COMPLETED,
                TransactionStage.FAILED,
                TransactionStage.CANCELED
            ):
                transaction.fail(component_id, e)
                self.update_transaction(transaction)
            
            # Re-raise the exception
            raise
