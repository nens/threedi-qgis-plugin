from ThreeDiToolbox.commands.base.custom_command import CustomCommandBase
from ThreeDiToolbox.model_checker.model_checker_view import \
    ModelCheckerDialogWidget


class CustomCommand(CustomCommandBase):

    def __init__(self, **kwargs):
        self.iface = kwargs.get('iface')
        self.modelchecker_widget = None

    def show_gui(self):
        """Show a GUI as a frontend for this script."""
        # Gui should allow the user to select a sqlite or postgis database
        # gui takes this command as an argument
        # If user presses 'accept/ok', it runs `run_it`

        self.modelchecker_widget = ModelCheckerDialogWidget(
            self.iface, command=self,
        )
        self.modelchecker_widget.exec_()  # block execution

    def run(self):
        """Entry point of CustomCommand. Either call show_gui or run_it here.
        """
        self.show_gui()

    def run_it(self, threedi_db):
        """Runs the script; this should contain the actual implementation of
        the script logic.
        """
        # db = ThreediDatabase(db_set, db_type)
        # mc = ModelChecker(db)
        # mc.parse_model()
        print('run the command!')