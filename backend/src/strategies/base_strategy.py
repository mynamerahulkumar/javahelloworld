"""
Base strategy interface for all trading strategies
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class StrategyStatus(Enum):
    """Strategy execution status"""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    All strategies must implement these methods.
    """
    
    def __init__(self, strategy_id: str, config: Dict[str, Any]):
        """
        Initialize strategy
        
        Args:
            strategy_id: Unique identifier for this strategy instance
            config: Strategy configuration dictionary
        """
        self.strategy_id = strategy_id
        self.config = config
        self.status = StrategyStatus.STOPPED
        self.error_message: Optional[str] = None
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the strategy execution
        
        Returns:
            True if started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the strategy execution
        
        Returns:
            True if stopped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current strategy status
        
        Returns:
            Dictionary containing status information
        """
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get strategy configuration
        
        Returns:
            Dictionary containing configuration
        """
        pass
    
    def get_id(self) -> str:
        """Get strategy instance ID"""
        return self.strategy_id
    
    def set_status(self, status: StrategyStatus, error_message: Optional[str] = None):
        """Update strategy status"""
        self.status = status
        if error_message:
            self.error_message = error_message
        if status == StrategyStatus.RUNNING and not self.start_time:
            import time
            self.start_time = time.time()
        if status == StrategyStatus.STOPPED and not self.stop_time:
            import time
            self.stop_time = time.time()







