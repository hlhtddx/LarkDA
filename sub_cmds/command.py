class Command():
    requires_workspace = True

    def __init__(self, workspace):
        self.workspace = workspace
        if workspace:
            self.drive = workspace.drive
        else:
            self.drive = None

    def validate_args(self, args) -> bool:
        return True
