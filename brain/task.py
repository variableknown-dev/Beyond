from dataclasses import dataclass, field


@dataclass
class Task:
    """
    Represents one action in a plan.
    """

    # Original user text
    text: str

    # Which skill should execute this?
    intent: str = "chat"

    # Action for the skill
    action: str = ""

    # Parameters for the action
    arguments: dict = field(default_factory=dict)

    # Execution status
    completed: bool = False
    success: bool = False

    # Skill output
    result: str = ""
