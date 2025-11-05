"""
Strategy manager for handling multiple strategy instances
"""
import uuid
import logging
import threading
from typing import Dict, Optional, List
from .base_strategy import BaseStrategy, StrategyStatus
from .breakout.breakout_service import BreakoutService

logger = logging.getLogger(__name__)


class StrategyManager:
    """
    Manages multiple strategy instances running simultaneously.
    Thread-safe operations for concurrent strategy management.
    """
    
    def __init__(self):
        """Initialize strategy manager"""
        self.strategies: Dict[str, BaseStrategy] = {}
        self.lock = threading.Lock()
        logger.info("StrategyManager initialized")
    
    def start_strategy(self, strategy_type: str, config: Dict) -> str:
        """
        Start a new strategy instance
        
        Args:
            strategy_type: Type of strategy ('breakout', etc.)
            config: Strategy configuration dictionary
            
        Returns:
            Strategy ID (UUID string)
        """
        strategy_id = str(uuid.uuid4())
        
        try:
            with self.lock:
                if strategy_type == 'breakout':
                    strategy = BreakoutService(strategy_id=strategy_id, config=config)
                else:
                    raise ValueError(f"Unknown strategy type: {strategy_type}")
                
                # Start the strategy
                if strategy.start():
                    self.strategies[strategy_id] = strategy
                    logger.info(f"Strategy {strategy_id} started successfully")
                    return strategy_id
                else:
                    raise RuntimeError(f"Failed to start strategy {strategy_id}")
                    
        except Exception as e:
            logger.error(f"Error starting strategy: {e}")
            raise
    
    def stop_strategy(self, strategy_id: str) -> bool:
        """
        Stop a specific strategy instance
        
        Args:
            strategy_id: Strategy ID to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            with self.lock:
                if strategy_id not in self.strategies:
                    logger.warning(f"Strategy {strategy_id} not found")
                    return False
                
                strategy = self.strategies[strategy_id]
                success = strategy.stop()
                
                if success:
                    # Keep strategy in dict for status queries, but mark as stopped
                    logger.info(f"Strategy {strategy_id} stopped successfully")
                
                return success
                
        except Exception as e:
            logger.error(f"Error stopping strategy {strategy_id}: {e}")
            return False
    
    def get_strategy(self, strategy_id: str) -> Optional[BaseStrategy]:
        """
        Get a strategy instance by ID
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Strategy instance or None if not found
        """
        with self.lock:
            return self.strategies.get(strategy_id)
    
    def get_all_strategies(self) -> List[Dict]:
        """
        Get list of all strategy instances with their status
        
        Returns:
            List of strategy status dictionaries
        """
        with self.lock:
            return [
                strategy.get_status()
                for strategy in self.strategies.values()
            ]
    
    def get_strategy_status(self, strategy_id: str) -> Optional[Dict]:
        """
        Get status of a specific strategy
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Status dictionary or None if not found
        """
        strategy = self.get_strategy(strategy_id)
        if strategy:
            return strategy.get_status()
        return None
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """
        Remove a strategy from the manager (after it's stopped)
        
        Args:
            strategy_id: Strategy ID to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            with self.lock:
                if strategy_id not in self.strategies:
                    return False
                
                strategy = self.strategies[strategy_id]
                
                # Ensure strategy is stopped before removing
                if strategy.status == StrategyStatus.RUNNING:
                    logger.warning(f"Cannot remove running strategy {strategy_id}, stopping first")
                    strategy.stop()
                
                del self.strategies[strategy_id]
                logger.info(f"Strategy {strategy_id} removed from manager")
                return True
                
        except Exception as e:
            logger.error(f"Error removing strategy {strategy_id}: {e}")
            return False
    
    def get_strategy_logs(self, strategy_id: str, limit: int = 100) -> Optional[str]:
        """
        Get logs from a specific strategy
        
        Args:
            strategy_id: Strategy ID
            limit: Maximum number of log lines
            
        Returns:
            Log string or None if strategy not found
        """
        strategy = self.get_strategy(strategy_id)
        if strategy and hasattr(strategy, 'get_logs'):
            return strategy.get_logs(limit=limit)
        return None


# Global strategy manager instance
_strategy_manager: Optional[StrategyManager] = None
_manager_lock = threading.Lock()


def get_strategy_manager() -> StrategyManager:
    """Get or create the global strategy manager instance"""
    global _strategy_manager
    with _manager_lock:
        if _strategy_manager is None:
            _strategy_manager = StrategyManager()
        return _strategy_manager

