import logging
import os

from threedi_modelchecker.model_checks import ThreediModelChecker
from threedi_modelchecker import exporters


from ThreeDiToolbox.commands.base.custom_command import CustomCommandBase
from ThreeDiToolbox.model_checker.model_checker_view import \
    ModelCheckerDialogWidget
from ThreeDiToolbox.utils.user_messages import pop_up_info


logger = logging.getLogger(__name__)


class CustomCommand(CustomCommandBase):

    def __init__(self, **kwargs):
        self.iface = kwargs.get('iface')
        self.modelchecker_widget = None
        self.plugin_dir = kwargs.get('plugin_dir')

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
        logger.info("Starting schematisation checker")

        model_checker = ThreediModelChecker(threedi_db)
        models_errors = model_checker.parse_model()

        output_filename = 'Model_errors.txt'
        output_file_path = os.path.join(
            self.plugin_dir, output_filename)
        exporters.export_to_file(models_errors, output_file_path)
        pop_up_info("Finished, see result in <a href='file:/%s'>%s</a>" %
                    (output_file_path, output_filename))
