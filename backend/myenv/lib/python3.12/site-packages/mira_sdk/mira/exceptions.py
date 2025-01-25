class FlowError(Exception):
    """Base exception for flow-related errors"""
    pass


class ValidationError(FlowError):
    """Raised when flow validation fails"""
    pass


class LoadError(FlowError):
    """Raised when flow loading fails"""
    pass
