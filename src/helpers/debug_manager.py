"""
Debug Manager for XOFlowers Conversational AI
Comprehensive logging and debugging system for all components
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Setup debug logging
debug_logger = logging.getLogger('xoflowers_debug')


@dataclass
class DebugEntry:
    """Single debug entry with timing and context"""
    timestamp: str
    component: str
    operation: str
    input_data: Any
    output_data: Any
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp,
            'component': self.component,
            'operation': self.operation,
            'input_data': str(self.input_data)[:500] if self.input_data else None,
            'output_data': str(self.output_data)[:500] if self.output_data else None,
            'execution_time': self.execution_time,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.metadata or {}
        }


class DebugManager:
    """
    Comprehensive debug manager for XOFlowers AI system
    Tracks all operations with detailed logging and timing
    """
    
    def __init__(self, debug_mode: bool = None):
        """
        Initialize debug manager
        
        Args:
            debug_mode: Enable debug mode (defaults to environment variable)
        """
        self.debug_mode = debug_mode if debug_mode is not None else os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.debug_entries: List[DebugEntry] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create debug directory
        self.debug_dir = Path("debug_logs")
        self.debug_dir.mkdir(exist_ok=True)
        
        # Setup file logging
        self.debug_file = self.debug_dir / f"debug_session_{self.session_id}.json"
        self.console_file = self.debug_dir / f"console_output_{self.session_id}.log"
        
        # Setup console logging
        if self.debug_mode:
            self._setup_console_logging()
            self.log_info("🐛 Debug mode enabled", "DebugManager", "initialization")
    
    def _setup_console_logging(self):
        """Setup console logging with proper formatting"""
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(self.console_file, encoding='utf-8')
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        debug_logger.setLevel(logging.DEBUG)
        debug_logger.addHandler(console_handler)
        debug_logger.addHandler(file_handler)
    
    def log_operation(self, 
                     component: str, 
                     operation: str, 
                     input_data: Any = None,
                     output_data: Any = None,
                     execution_time: float = 0.0,
                     success: bool = True,
                     error_message: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """
        Log a debug operation
        
        Args:
            component: Component name (e.g., 'ChromaDB', 'AI_Engine')
            operation: Operation name (e.g., 'search_products', 'classify_intent')
            input_data: Input data for the operation
            output_data: Output data from the operation
            execution_time: Time taken for operation in seconds
            success: Whether operation was successful
            error_message: Error message if operation failed
            metadata: Additional metadata
        """
        if not self.debug_mode:
            return
        
        entry = DebugEntry(
            timestamp=datetime.now().isoformat(),
            component=component,
            operation=operation,
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
        
        self.debug_entries.append(entry)
        
        # Console output
        status = "✅" if success else "❌"
        debug_logger.info(f"{status} {component}.{operation} ({execution_time:.3f}s)")
        
        if input_data and self.debug_mode:
            debug_logger.debug(f"   Input: {str(input_data)[:200]}...")
        
        if output_data and self.debug_mode:
            debug_logger.debug(f"   Output: {str(output_data)[:200]}...")
        
        if error_message:
            debug_logger.error(f"   Error: {error_message}")
        
        # Save to file periodically
        if len(self.debug_entries) % 10 == 0:
            self._save_debug_file()
    
    def log_info(self, message: str, component: str = "System", operation: str = "info"):
        """Log an info message"""
        if self.debug_mode:
            debug_logger.info(f"ℹ️ {component}: {message}")
            
            self.log_operation(
                component=component,
                operation=operation,
                input_data=message,
                success=True
            )
    
    def log_warning(self, message: str, component: str = "System", operation: str = "warning"):
        """Log a warning message"""
        if self.debug_mode:
            debug_logger.warning(f"⚠️ {component}: {message}")
            
            self.log_operation(
                component=component,
                operation=operation,
                input_data=message,
                success=True,
                metadata={'level': 'warning'}
            )
    
    def log_error(self, message: str, component: str = "System", operation: str = "error", error: Exception = None):
        """Log an error message"""
        if self.debug_mode:
            debug_logger.error(f"❌ {component}: {message}")
            if error:
                debug_logger.error(f"   Exception: {str(error)}")
            
            self.log_operation(
                component=component,
                operation=operation,
                input_data=message,
                success=False,
                error_message=str(error) if error else message,
                metadata={'level': 'error'}
            )
    
    def time_operation(self, component: str, operation: str):
        """Context manager for timing operations"""
        return DebugTimer(self, component, operation)
    
    def get_debug_summary(self) -> Dict[str, Any]:
        """Get summary of debug session"""
        if not self.debug_entries:
            return {'message': 'No debug entries recorded'}
        
        total_operations = len(self.debug_entries)
        successful_operations = sum(1 for entry in self.debug_entries if entry.success)
        failed_operations = total_operations - successful_operations
        
        # Component statistics
        component_stats = {}
        for entry in self.debug_entries:
            if entry.component not in component_stats:
                component_stats[entry.component] = {'total': 0, 'success': 0, 'failed': 0, 'avg_time': 0}
            
            component_stats[entry.component]['total'] += 1
            if entry.success:
                component_stats[entry.component]['success'] += 1
            else:
                component_stats[entry.component]['failed'] += 1
            
            component_stats[entry.component]['avg_time'] += entry.execution_time
        
        # Calculate averages
        for component, stats in component_stats.items():
            if stats['total'] > 0:
                stats['avg_time'] = stats['avg_time'] / stats['total']
        
        return {
            'session_id': self.session_id,
            'debug_mode': self.debug_mode,
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'component_stats': component_stats,
            'debug_file': str(self.debug_file),
            'console_file': str(self.console_file)
        }
    
    def _save_debug_file(self):
        """Save debug entries to JSON file"""
        try:
            debug_data = {
                'session_info': {
                    'session_id': self.session_id,
                    'debug_mode': self.debug_mode,
                    'timestamp': datetime.now().isoformat(),
                    'total_entries': len(self.debug_entries)
                },
                'entries': [entry.to_dict() for entry in self.debug_entries],
                'summary': self.get_debug_summary()
            }
            
            with open(self.debug_file, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            debug_logger.error(f"Failed to save debug file: {e}")
    
    def save_and_close(self):
        """Save final debug file and close session"""
        if self.debug_mode:
            self._save_debug_file()
            summary = self.get_debug_summary()
            
            debug_logger.info("🎯 Debug Session Summary:")
            debug_logger.info(f"   Total Operations: {summary['total_operations']}")
            debug_logger.info(f"   Success Rate: {summary['success_rate']:.2%}")
            debug_logger.info(f"   Debug File: {summary['debug_file']}")
            debug_logger.info(f"   Console Log: {summary['console_file']}")


class DebugTimer:
    """Context manager for timing operations"""
    
    def __init__(self, debug_manager: DebugManager, component: str, operation: str):
        self.debug_manager = debug_manager
        self.component = component
        self.operation = operation
        self.start_time = None
        self.input_data = None
        self.metadata = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        self.debug_manager.log_operation(
            component=self.component,
            operation=self.operation,
            input_data=self.input_data,
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            metadata=self.metadata
        )
    
    def set_input(self, input_data: Any):
        """Set input data for the operation"""
        self.input_data = input_data
        return self
    
    def set_metadata(self, **kwargs):
        """Set metadata for the operation"""
        self.metadata.update(kwargs)
        return self


# Global debug manager instance
_debug_manager = None

def get_debug_manager() -> DebugManager:
    """Get the global debug manager instance"""
    global _debug_manager
    if _debug_manager is None:
        _debug_manager = DebugManager()
    return _debug_manager

def enable_debug_mode():
    """Enable debug mode globally"""
    global _debug_manager
    _debug_manager = DebugManager(debug_mode=True)
    return _debug_manager

def disable_debug_mode():
    """Disable debug mode globally"""
    global _debug_manager
    if _debug_manager:
        _debug_manager.debug_mode = False