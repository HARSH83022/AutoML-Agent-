"""
Logging configuration for AutoML Orchestrator
Provides structured logging with sanitization of sensitive data
"""
import logging
import sys
import re
from typing import Any, Dict
from app.config import Config


# Patterns for sensitive data that should be sanitized
SENSITIVE_PATTERNS = [
    (re.compile(r'(api[_-]?key["\s:=]+)([^\s,}"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(password["\s:=]+)([^\s,}"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(token["\s:=]+)([^\s,}"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(secret["\s:=]+)([^\s,}"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(authorization["\s:]+bearer\s+)([^\s,}"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(sk-[a-zA-Z0-9]{20,})', re.IGNORECASE), r'***REDACTED***'),  # OpenAI keys
    (re.compile(r'(sk-ant-[a-zA-Z0-9-]{20,})', re.IGNORECASE), r'***REDACTED***'),  # Anthropic keys
]


class SanitizingFormatter(logging.Formatter):
    """
    Custom formatter that sanitizes sensitive information from log messages
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Sanitize the message
        original_msg = record.getMessage()
        sanitized_msg = self.sanitize(original_msg)
        record.msg = sanitized_msg
        record.args = ()
        
        # Format the record
        formatted = super().format(record)
        
        return formatted
    
    @staticmethod
    def sanitize(text: str) -> str:
        """
        Remove sensitive information from text
        """
        if not isinstance(text, str):
            text = str(text)
        
        for pattern, replacement in SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        
        return text


def setup_logging():
    """
    Configure logging for the application
    """
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatter
    if Config.APP_ENV == "production":
        # Production: JSON-like structured logging
        log_format = '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
    else:
        # Development: Human-readable logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = SanitizingFormatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    """
    return logging.getLogger(name)


def log_request(request_id: str, method: str, path: str, **kwargs):
    """
    Log an HTTP request with sanitization
    """
    logger = get_logger("api.request")
    sanitized_kwargs = {k: SanitizingFormatter.sanitize(str(v)) for k, v in kwargs.items()}
    logger.info(f"Request {request_id}: {method} {path} {sanitized_kwargs}")


def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log an error with context, sanitizing sensitive information
    """
    logger = get_logger("api.error")
    error_msg = str(error)
    sanitized_msg = SanitizingFormatter.sanitize(error_msg)
    
    if context:
        sanitized_context = {k: SanitizingFormatter.sanitize(str(v)) for k, v in context.items()}
        logger.error(f"Error: {sanitized_msg} | Context: {sanitized_context}", exc_info=True)
    else:
        logger.error(f"Error: {sanitized_msg}", exc_info=True)


# Initialize logging on module import
setup_logging()
