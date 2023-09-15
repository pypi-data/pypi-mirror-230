import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from egse.bits import bit_set
from egse.fee.nfee import HousekeepingData
from egse.gui.led import Indic
from egse.gui.led import LED
from egse.spw import HousekeepingPacket

try:
    _ = os.environ["PLATO_CAMERA_IS_EM"]
    PLATO_CAMERA_IS_EM = True if _.capitalize() in ("1", "True", "Yes") else 0
except KeyError:
    PLATO_CAMERA_IS_EM = False


class _CCDVoltages(QGroupBox):

    def __init__(self, *args, **kwargs):
        super().__init__("CCD Voltages", *args, **kwargs)

        self._fields = {}

        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        for col, name in enumerate(["CCD1", "CCD2", "CCD3", "CCD4"]):
            label = QLabel(name)
            label.setAlignment(Qt.AlignHCenter)
            layout.addWidget(label, 0, col * 2 + 1)

        self.ccd_fields_layout = [{}, {}, {}, {}]

        for ccd_number in range(1, 5):
            if PLATO_CAMERA_IS_EM:
                self.ccd_fields_layout[ccd_number - 1]["VOD"] = [f"CCD{ccd_number}_VOD_MON", 1, 2 * (ccd_number - 1)]
                index = 2
            else:
                self.ccd_fields_layout[ccd_number - 1]["VOD_E"] = [f"CCD{ccd_number}_VOD_MON_E", 1, 2 * (ccd_number - 1)]
                self.ccd_fields_layout[ccd_number - 1]["VOD_F"] = [f"CCD{ccd_number}_VOD_MON_F", 2, 2 * (ccd_number - 1)]
                index = 3

            self.ccd_fields_layout[ccd_number - 1]["VOG"] = [f"CCD{ccd_number}_VOG_MON", index, 2 * (ccd_number - 1)]
            index += 1
            self.ccd_fields_layout[ccd_number - 1]["VDD"] = [f"CCD{ccd_number}_VDD_MON", index, 2 * (ccd_number - 1)]
            index += 1
            self.ccd_fields_layout[ccd_number - 1]["VGD"] = [f"CCD{ccd_number}_VGD_MON", index, 2 * (ccd_number - 1)]
            index += 1
            self.ccd_fields_layout[ccd_number - 1]["VRD_E"] = [f"CCD{ccd_number}_VRD_MON_E", index, 2 * (ccd_number - 1)]
            index += 1
            self.ccd_fields_layout[ccd_number - 1]["VRD_F"] = [f"CCD{ccd_number}_VRD_MON_F", index, 2 * (ccd_number - 1)]

        for fields in (self.ccd_fields_layout):
            for par, x in fields.items():
                self._fields[x[0]] = field = QLineEdit()
                field.setMinimumWidth(60)
                field.setAlignment(Qt.AlignRight)
                field.setReadOnly(True)
                label = QLabel(str(par))
                label.setAlignment(Qt.AlignRight)
                layout.addWidget(label, x[1], x[2])
                layout.addWidget(field, x[1], x[2] + 1)

        self.setLayout(layout)

    @property
    def fields(self):
        return self._fields


class _NFEETemperatures(QGroupBox):
    N_FEE_FIELDS_LAYOUT = {
        "PRT1": ["PRT1", 1, 0],
        "PRT2": ["PRT2", 2, 0],
        "PRT3": ["PRT3", 3, 0],
        "PRT4": ["PRT4", 4, 0],
        "PRT5": ["PRT5", 5, 0],

        "CCD1": ["CCD1_TS", 1, 2],
        "CCD2": ["CCD2_TS", 2, 2],
        "CCD3": ["CCD3_TS", 3, 2],
        "CCD4": ["CCD4_TS", 4, 2],

        "T_A": ["TSENSE_A", 6, 0],
        "T_B": ["TSENSE_B", 6, 2],
    }

    def __init__(self, *args, **kwargs):
        super().__init__("Temperatures", *args, **kwargs)

        self._fields = {}

        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # The next line is to line-up with the CCD Voltages which have header

        layout.addWidget(QLabel(), 0, 0)

        for par, x in self.N_FEE_FIELDS_LAYOUT.items():
            self._fields[x[0]] = field = QLineEdit()
            field.setMinimumWidth(60)
            field.setAlignment(Qt.AlignRight)
            field.setReadOnly(True)
            label = QLabel(str(par))
            label.setAlignment(Qt.AlignRight)
            layout.addWidget(label, x[1], x[2])
            layout.addWidget(field, x[1], x[2] + 1)

        self.setLayout(layout)

    @property
    def fields(self):
        return self._fields


class _SpaceWireStatus(QGroupBox):
    N_FEE_FIELDS_LAYOUT = {
        "op_mode": [0, 0],
        "frame_counter": [1, 0],
        "frame_number": [2, 0],
        "FPGA minor version": [0, 2],
        "FPGA major version": [1, 2],
        "Board ID": [2, 2],
        "spw_timecode": [0, 4],
    }

    def __init__(self, *args, **kwargs):
        super().__init__("SpW Status", *args, **kwargs)

        self._fields = {}

        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        for par, x in self.N_FEE_FIELDS_LAYOUT.items():
            self._fields[par] = field = QLineEdit()
            field.setAlignment(Qt.AlignRight)
            field.setReadOnly(True)
            layout.addWidget(QLabel(par), x[0], x[1])
            layout.addWidget(field, x[0], x[1] + 1)

        self.setLayout(layout)

    @property
    def fields(self):
        return self._fields


class _TOUSensors(QGroupBox):
    N_FEE_FIELDS_LAYOUT = {
        1: [0, 0],
        2: [1, 0],
        3: [2, 0],
        4: [0, 2],
        5: [1, 2],
        6: [2, 2],
    }

    def __init__(self, *args, **kwargs):
        super().__init__("TOU Sensors", *args, **kwargs)

        self._fields = {}

        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        for par, x in self.N_FEE_FIELDS_LAYOUT.items():
            self._fields[par] = field = QLineEdit()
            field.setMinimumWidth(60)
            field.setAlignment(Qt.AlignRight)
            field.setReadOnly(True)
            layout.addWidget(QLabel(str(par)), x[0], x[1])
            layout.addWidget(field, x[0], x[1] + 1)

        self.setLayout(layout)

    @property
    def fields(self):
        return self._fields


class _NFEEVoltages(QGroupBox):

    def __init__(self, *args, **kwargs):
        super().__init__("N-FEE Voltages", *args, **kwargs)

        self.voltage_fields_layout = {
            "3V3D": ["3V3D_MON", 0, 0],
            "2V5D": ["2V5D_MON", 1, 0],
            "1V5D": ["1V5D_MON", 2, 0],
            "5VREF": ["5VREF_MON", 3, 0],

            "-5VB": ["5VB_NEG_MON", 1, 2],
            "3V3B": ["3V3B_MON", 0, 2],
            "2V5A": ["2V5A_MON", 3, 2],

            "VICLK": ["VICLK", 0, 4],
            "VRCLK_MON": ["VRCLK_MON", 1, 4],
            "VCCD": ["VCCD", 2, 4],

            "VCCD_RAW": ["VCCD_POS_RAW", 2-2, 6],
            "VCLK_RAW": ["VCLK_POS_RAW", 3-2, 6],
            "ZERO_DIFF_AMP": ["ZERO_DIFF_AMP", 4-2, 6],
            "VAN1_RAW": ["VAN1_POS_RAW", 0, 8],
            "VAN2_RAW": ["VAN2_POS_RAW", 1, 8],
            "−VAN3_MON": ["VAN3_NEG_MON", 2, 8],
            "VDIG_RAW": ["VDIG_RAW", 3, 8],
        }

        if PLATO_CAMERA_IS_EM:
            self.voltage_fields_layout["+5VB"] = ["5VB_POS_MON", 0, 2]
            self.voltage_fields_layout["VICLK_LOW"] = ["VICLK_LOW", 3, 4]
            self.voltage_fields_layout["VRCLK_LOW"] = ["VRCLK_LOW", 4, 4]
            self.voltage_fields_layout["VDIG_RAW_2"] = ["VDIG_RAW_2", 4, 8]
        else:
            self.voltage_fields_layout["1V8D"] = ["1V8D_MON", 4, 2]

        self._fields = {}

        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        for par, x in self.voltage_fields_layout.items():
            self._fields[x[0]] = field = QLineEdit()
            field.setMinimumWidth(60)
            field.setAlignment(Qt.AlignRight)
            field.setReadOnly(True)
            label = QLabel(str(par))
            label.setAlignment(Qt.AlignRight)
            layout.addWidget(label, x[1], x[2])
            layout.addWidget(field, x[1], x[2] + 1)

        self.setLayout(layout)

    @property
    def fields(self):
        return self._fields


class _SpWLEDWidget(QGroupBox):

    def __init__(self, *args, **kwargs):

        super().__init__("SpW Status", *args, **kwargs)

        self._leds = [
            [QLabel("Running"), LED(self), Indic.GREEN,
                "SpaceWire link is running"],  # bit 0
            [QLabel("Disconnect"), LED(self), Indic.ORANGE,
                "SpaceWire link is disconnected"],  # bit 1
            [QLabel("Parity Error"), LED(self), Indic.RED,
                "A parity error occurred on the SpW link"],  # bit 2
            [QLabel("Credit Error"), LED(self), Indic.RED,
                "A credit error occurred on the SpW link"],  # bit 3
            [QLabel("Escape Error"), LED(self), Indic.RED,
                "An escape error occurred on the SpW link"],  # bit 4
            [QLabel("RMAP Target Indicate"), LED(self), Indic.ORANGE,
                ""],  # bit 5
        ]

        vbox = QVBoxLayout()

        for led in self._leds:

            # Set tooltips for the LEDs

            led[1].setToolTip(led[3])

            # Create a hbox where the led and the label is added, then add this hbox to the
            # states vbox.

            hbox = QHBoxLayout()
            hbox.addWidget(led[1])
            hbox.addWidget(led[0])

            # Add the corresponding hbox to the states vbox

            vbox.addLayout(hbox)

        # Make sure the hboxes stay nicely together when vertically resizing the Frame.

        vbox.addStretch()

        self.setLayout(vbox)

    def update_leds(self, status: int) -> None:

        for idx, led in enumerate(self._leds):
            if bit_set(status, idx):
                led[1].set_color(led[2])
            else:
                led[1].set_color(Indic.BLACK)


class _ErrorFlagsWidget(QGroupBox):

    def __init__(self, *args, **kwargs):

        super().__init__("Error Flags", *args, **kwargs)

        self._leds = [
            [QLabel("Wrong X-Coordinate"), LED(self), Indic.RED,
                "Window Pixels fall outside CDD boundary due to wrong x-coordinate"],  # bit 0
            [QLabel("Wrong Y-Coordinate"), LED(self), Indic.RED,
                "Window Pixels fall outside CDD boundary due to wrong y-coordinate"],  # bit 1
            [QLabel("E SRAM Full"), LED(self), Indic.RED,
                "E-Side pixel external SRAM BUFFER  is Full"],  # bit 2
            [QLabel("F SRAM Full"), LED(self), Indic.RED,
                "F-Side pixel external SRAM BUFFER  is Full"],  # bit 3
            [QLabel("AWLA Error"), LED(self), Indic.RED,
                "Too many overlapping windows, could not complete awla, "
                "some pixels touching the window will be dropped."],  # bit 4
            [QLabel("SRAM EDAC Correct"), LED(self), Indic.RED,
                "SRAM EDAC Correctable "],  # bit 5
            [QLabel("SRAM EDAC Uncorrect"), LED(self), Indic.RED,
                "SRAM EDAC Uncorrectable "],  # bit 6
            [QLabel("Block R EDAC"), LED(self), Indic.RED,
                "BLOCK RAM EDAC Uncorrectable  TBC"],  # bit 7
            [QLabel("Disconnect Error"), LED(self), Indic.RED, "Link Disconnect Error"],  # bit 8
            [QLabel("Escape Error"), LED(self), Indic.RED, "Link Escape Error"],  # bit 9
            [QLabel("Credit Error"), LED(self), Indic.RED, "Link Credit Error"],  # bit 10
            [QLabel("Parity Error"), LED(self), Indic.RED, "Link Parity Error"],  # bit 11
            [QLabel("Lock Error"), LED(self), Indic.RED, "PLL Lock Error"],  # bit 12
        ]

        vbox = QVBoxLayout()

        for led in self._leds:

            # Set tooltips for the LEDs

            led[1].setToolTip(led[3])

            # Create a hbox where the led and the label is added, then add this hbox to the
            # states vbox.

            hbox = QHBoxLayout()
            hbox.addWidget(led[1])
            hbox.addWidget(led[0])

            # Add the corresponding hbox to the states vbox

            vbox.addLayout(hbox)

        # Make sure the hboxes stay nicely together when vertically resizing the Frame.

        vbox.addStretch()

        self.setLayout(vbox)

    def update_flags(self, error_flags: int) -> None:
        for idx, led in enumerate(self._leds):
            if bit_set(error_flags, idx):
                led[1].set_color(led[2])
            else:
                led[1].set_color(Indic.BLACK)


class NFEEHousekeepingWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._spw_status = _SpaceWireStatus()
        self._tou_sense = _TOUSensors()
        self._n_fee_voltages = _NFEEVoltages()
        self._n_fee_temperatures = _NFEETemperatures()
        self._ccd_voltages = _CCDVoltages()
        self._spw_leds = _SpWLEDWidget()
        self._error_flags = _ErrorFlagsWidget()

        hbox_1 = QHBoxLayout()
        hbox_1.addWidget(self._n_fee_temperatures)
        hbox_1.addWidget(self._ccd_voltages)

        hbox_2 = QHBoxLayout()
        hbox_2.addWidget(self._tou_sense)
        hbox_2.addWidget(self._spw_status)

        vbox_1 = QVBoxLayout()
        vbox_1.addWidget(self._error_flags)
        vbox_1.addWidget(self._spw_leds)
        vbox_1.addStretch()

        vbox_2 = QVBoxLayout()
        vbox_2.addLayout(hbox_1)
        vbox_2.addWidget(self._n_fee_voltages)
        vbox_2.addLayout(hbox_2)
        vbox_2.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_1)
        hbox.addLayout(vbox_2)

        self.setLayout(hbox)

    @property
    def spw_status(self):
        return self._spw_status

    @property
    def tou_sense(self):
        return self._tou_sense

    @property
    def n_fee_voltages(self):
        return self._n_fee_voltages

    @property
    def n_fee_temperatures(self):
        return self._n_fee_temperatures

    @property
    def ccd_voltages(self):
        return self._ccd_voltages

    @property
    def spw_leds(self):
        return self._spw_leds

    @property
    def error_flags(self):
        return self._error_flags

    def update_fields(self, packet: HousekeepingPacket):

        hk_data = HousekeepingData(packet.data)

        fields = self.spw_status.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.tou_sense.fields
        for par in fields:
            x = f"TOU_SENSE_{par}"
            fields[par].setText(f"{hk_data[x]}")

        fields = self.n_fee_voltages.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.n_fee_temperatures.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.ccd_voltages.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        self.spw_leds.update_leds(hk_data["spw_status"])

        self.error_flags.update_flags(hk_data["error_flags"])

        self.repaint()
