"""Custom exception types."""


class NaNError(Exception):
    """Raised when NaNs are detected in the model parameters."""


class EpochDoneError(Exception):
    """Raised when an epoch is done."""


class TrainingFinishedError(Exception):
    """Raised when training is finished."""


class MinGradScaleError(TrainingFinishedError):
    """Raised when the minimum gradient scale is reached.

    This is a subclass of :class:`TrainingFinishedError` because it indicates
    that training is finished and causes the post-training hooks to be run.
    """
