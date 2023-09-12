"""
Class Connection: trace connections in control system by preserving original `System` objects and connection type.

| Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
| Saurav Bania <saurav[dot]bania[at]studium.uni-hamburg.de>

"""


class Connection:
    def __init__(self, sys1, sys2, type):
        """Constructor takes two System objects and creates Connection object, which references both systems and connection type.

        Parameters
        ----------
        sys1 : `System`, `control.TransferFunction`
            input control system
        sys2 : `System`, `control.TransferFunction`
            input control system
        type : str

        """

        self.sys1 = sys1
        self.sys2 = sys2
        self.type = type
