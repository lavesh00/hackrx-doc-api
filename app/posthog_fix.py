"""
PostHog Telemetry Fix for ChromaDB 1.0.5
Monkey patches PostHog module before ChromaDB can import it
"""
import sys
from typing import Any, Dict, Optional

class MockPostHog:
    """Mock PostHog client that silently handles all telemetry calls"""
    
    def __init__(self, *args, **kwargs):
        pass
    
    def capture(self, *args, **kwargs) -> None:
        """Mock capture method - does nothing"""
        pass
    
    def identify(self, *args, **kwargs) -> None:
        """Mock identify method - does nothing"""
        pass
    
    def group(self, *args, **kwargs) -> None:
        """Mock group method - does nothing"""
        pass
    
    def flush(self, *args, **kwargs) -> None:
        """Mock flush method - does nothing"""
        pass
    
    def feature_enabled(self, *args, **kwargs) -> bool:
        """Mock feature_enabled method - always returns False"""
        return False
    
    def close(self, *args, **kwargs) -> None:
        """Mock close method - does nothing"""
        pass

class MockPostHogModule:
    """Mock PostHog module with all expected attributes"""
    
    def __init__(self):
        self.Posthog = MockPostHog
        
    def capture(self, *args, **kwargs) -> None:
        pass
        
    def identify(self, *args, **kwargs) -> None:
        pass
    
    def group(self, *args, **kwargs) -> None:
        pass
    
    def flush(self, *args, **kwargs) -> None:
        pass

# Install the mock before any ChromaDB imports
if 'posthog' not in sys.modules:
    sys.modules['posthog'] = MockPostHogModule()
    print("🔧 PostHog telemetry disabled via monkey patching")