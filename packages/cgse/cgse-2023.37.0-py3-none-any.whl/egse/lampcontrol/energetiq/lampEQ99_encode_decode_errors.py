from typing import List, Dict

LAMP_ERRORS = {
    0: ("No error", "No error was reported."),
    3: ("Factory EE bad", "Error reading the factory data."),
    4: ("User EE bad", "Error reading the user data, unit reset to factory defaults."),
    5: ("User reset", "Unit reset to factory defaults (not an error, notification only)."),
    6: ("User EE bad, no recovery", "Error reading the user data, could not be reset to factory defaults."),
    10: ("Access denied", "Attempt to change protected settings without authorization."),
    100: (
    "General Error", "The error code is non-specific, and is generally used when no other error code is suitable."),
    102: ("Message too long", "The message is too long to process (USB/Serial only)."),
    123: ("Path not found", "The message used an invalid path command (USB/Serial only)."),
    127: ("Change not allowed", "Attempt to change locked value."),
    201: ("Data out of range",
    "The message attempted to set a value that was outside the allowable range (USB/Serial only)."),
    202: (
    "Invalid data type", "When trying to parse the message, the data was in an invalid format (USB/Serial only)."),
    303: ("Input buffer overflow", "Data was sent to the instrument faster than it could process."),
    600: ("Interlock", "The interlock input is open."),
    601: ("Lamp fault", "The controller is indicating a lamp fault. "
                        "Consult the EQ-99 User’s Manual for more information."),
    602: ("Controller fault", "The controller is indicating a controller fault. "
                              "This is often caused by an open interlock condition. "
                              "If that is not the case, consult the EQ-99 User’s Manual for more information."),
    603: ("No controller", "The EQ-99 Power Supply Controller was not detected."),
    998: ("Command not supported", "A command was recognized but not supported by the instrument."),
    999: ("Non-specific error", "A non-specific error was encountered."),
}
LAMP_ERROR_CODES = list(LAMP_ERRORS.keys())


def encode_lamp_errors(errors: List[int]) -> int:
    """
    Encodes the list of lamp error codes into a bitfield. The bitfield is constructed from the order of the keys
    in the LAMP_ERRORS dictionary.

    Note: when you need to add additional keys, add them at the end of the dictionary. This will guarantee proper
    decoding of previously encoded lamp errors.

    Args:
        errors: a list of error codes as integers

    Returns:
        A integer representing the error codes as a bitfield.
    """
    encoded_errors = 0

    for error in errors:
        idx = LAMP_ERROR_CODES.index(error)
        encoded_errors |= 2 ** idx

    return encoded_errors


def decode_lamp_errors(errors: int) -> Dict[int, str]:
    """
    Decodes the bitfield into the error codes and their messages.

    Args:
        errors: an integer as a bitfield of lamp errors (previously encoded with encode_lamp_errors)

    Returns:
        A dictionary of the lamp errors (key is error code, value is the description)
    """
    result = {}

    for shift in range(len(LAMP_ERRORS)):
        if (errors >> shift) & 1:
            error_code = LAMP_ERROR_CODES[shift]
            result[error_code] = ": ".join(LAMP_ERRORS[error_code])

    return result
