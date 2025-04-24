"""
AeroLearn AI - Aerospace Engineering Education Platform
Version: 0.1.0
Created: 2025-04-24

An AI-first education system for Aerospace Engineering that enhances teaching
and learning experiences through intelligent content management, personalized
learning assistance, and comprehensive analytics.
"""

__version__ = "0.1.0"

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
 level=os.getenv("LOG_LEVEL", "INFO"),
 format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
 handlers=[
     logging.StreamHandler(),
     logging.FileHandler("aerolearn_ai.log"),
 ],
)

logger = logging.getLogger(__name__)
logger.info("AeroLearn AI initializing...")
