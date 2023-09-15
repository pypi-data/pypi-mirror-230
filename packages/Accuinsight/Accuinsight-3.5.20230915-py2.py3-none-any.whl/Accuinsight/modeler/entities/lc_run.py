from Accuinsight.modeler.entities._modeler_object import _ModelerObject


class Run(_ModelerObject):
    """
    Run object.
    """

    def __init__(self, run_id):
        self._run_id = run_id

    @property
    def run_id(self):
        """
        The run id that is returned by back-end server.

        """
        return self._run_id