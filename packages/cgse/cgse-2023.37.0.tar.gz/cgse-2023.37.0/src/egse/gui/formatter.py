def degree_formatter(angle, dummy=None):

        """
        Formatting of the given angle to a string showing the angle as an
        integer, followed by a degreee sign.

        :param angle: Angle to format [degrees].
        """

        return "{}".format(str(angle if angle % 1 else int(angle))) + u"\u00B0"
