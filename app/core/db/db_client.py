"""
Database Client for AeroLearn AI
Handles SQLAlchemy engine and session management.
Edit DB_URL in schema.py as required for different environments.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
import threading
from contextlib import contextmanager

class DBClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_url):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBClient, cls).__new__(cls)
                cls._instance._initialize(db_url)
            return cls._instance

    def _initialize(self, db_url):
        # Set expire_on_commit=False to prevent DetachedInstanceError
        self.engine = create_engine(db_url, echo=False, future=True)
        self.SessionLocal = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False  # Prevents DetachedInstanceError
            )
        )

    def get_session(self):
        """
        Returns a new SQLAlchemy session.
        Remember to close() or use as context manager.
        """
        return self.SessionLocal()

    def dispose(self):
        self.engine.dispose()
        self.SessionLocal.remove()
        
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def get_by_id(self, model, object_id, eager_relations=None):
        """
        Get an object by its primary key ID.
        Optionally eagerly loads given relationship attributes, using loader options.

        Args:
            model: SQLAlchemy ORM class.
            object_id: ID (primary key) of object to fetch.
            eager_relations: (optional) list of SQLAlchemy loader options, e.g. [joinedload(Model.relationship)]
        """
        with self.session_scope() as session:
            query = session.query(model)
            if eager_relations:
                query = query.options(*eager_relations)
            return query.get(object_id)
            
    def add_object(self, obj):
        """Add a new object to the database."""
        with self.session_scope() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
            
    def update_object(self, obj):
        """Update an existing object in the database."""
        with self.session_scope() as session:
            session.merge(obj)
            session.commit()
            return obj
            
    def delete_object(self, obj):
        """Delete an object from the database."""
        with self.session_scope() as session:
            session.delete(obj)
            
    def search(self, model, **kwargs):
        """Search for objects matching the given criteria."""
        with self.session_scope() as session:
            return session.query(model).filter_by(**kwargs).all()
            
    def execute_query(self, query_func):
        """Execute a custom query function within a session context."""
        with self.session_scope() as session:
            return query_func(session)

# Usage:
# from app.core.db.db_client import DBClient
# db = DBClient("sqlite:///app_database.db")
# session = db.get_session()
# ... use session ...
# session.close()
