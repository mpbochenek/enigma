from collections import deque
from typing import List, Set


class Enigma:
    """
    The Enigma class that combines all elements - plugboard, rotors and reflector
    """

    def __init__(self):
        self.plugboard: Plugboard = None
        self.drum: List[Rotor] = []
        self.reflector = None

        self.wiring = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def encode_sequence(self, a_string):
        """
        Method that decodes/encodes a message in a form of a string
        :param a_string: message to be decoded/encoded
        :return: decoded/encoded message
        """
        encoded = ''

        if len(self.drum) < 3:
            raise MissingRotors('Enigma must contain at least three rotors')

        # helper variable that prevents third rotor rotation when on notch position
        if type(self.drum[2].notch) is int and self.drum[2].notch == self.wiring.index(self.drum[2].label[2]) - 1:
            third_notch_rotation = True
        else:
            third_notch_rotation = False

        for letter in a_string:
            self.drum[0].rotate_rotor()
            if type(self.drum[0].notch) is int and self.drum[0].notch == self.wiring.index(self.drum[0].label[0]):
                self.drum[1].rotate_rotor()
                self.drum[1].set_rotor_offset(1)
                third_notch_rotation = True
            if type(self.drum[0].notch) is int and self.drum[1].notch - 1 == (self.wiring.index(self.drum[1].label[0])):
                self.drum[1].rotate_rotor()
                self.drum[1].set_rotor_offset(1)
            if type(self.drum[1].notch) is int and self.drum[1].notch == self.wiring.index(self.drum[1].label[0]) \
                    and third_notch_rotation:
                self.drum[2].rotate_rotor()
                third_notch_rotation = False

            contact = self.wiring.index(self.plugboard.encode(letter))

            # simulates current flow from right to left
            for rotor_number in range(len(self.drum)):
                contact = self.drum[rotor_number].label.index(self.drum[rotor_number].rotor_wiring[contact])
            # reflector
            contact = self.reflector.encode(self.wiring[contact])
            # simulates current flow from left to right
            for rotor_number in range(len(self.drum) - 1, -1, -1):
                contact = self.drum[rotor_number].rotor_wiring.index(self.drum[rotor_number].label[contact])
            # plugboard
            encoded += self.plugboard.encode(self.wiring[contact])
            self.drum[0].set_rotor_offset(1)

        # deque needs to be defaulted before rotors are exchanged
        for r in self.drum:
            r.reset_deque()
        return encoded

    def add_rotor(self, rotor):
        """
        Method that adds rotor to Enigma's drum.
        For consistency with the way rotors' types, setting and positions are provided,
        the rotors are added from left to right.
        :param rotor: Rotor object
        :return: void
        """
        if len(self.drum) > 3:
            raise EnigmaDrumFull('Maximum of 4 rotors can be added')
        self.drum.append(rotor)

    def set_reflector(self, reflector):
        """
        Method that sets the reflector of a given type
        :param reflector: Reflector object
        :return: void
        """
        self.reflector = reflector

    def set_plugboard(self, plugboard):
        """
        Method that sets the plugboard
        :param plugboard: Plugboard object
        :return: void
        """
        self.plugboard = plugboard


class PlugLead:
    """
    PlugLead class that models a single plugs connection
    """

    def __init__(self, mapping):
        self.lead_mapping: Set[str] = set()
        if type(mapping) == str and len(mapping) == 2 and (mapping[0].isalpha() and mapping[1].isalpha()):
            self.lead_mapping.add(mapping[0].upper())
            self.lead_mapping.add(mapping[1].upper())

    def encode(self, character):
        """
        Method that encodes a single plugs pair
        :param character: a character to be encoded
        :return: character: encoded string
        """
        if character in self.lead_mapping:
            encoded = self.lead_mapping.difference(character)
            return encoded.pop()
        return character

    def get_mapping(self):
        """
        Getter method
        :return: lead_mapping
        """
        return self.lead_mapping

    def __str__(self):
        """
        Overridden method for textual representation of PlugLead
        Used for debugging
        :return: lead_mapping
        """
        mapping = list(self.lead_mapping)
        map_to_str = mapping[0] + mapping[1]
        return f"{map_to_str}"


class Plugboard:
    """
    Plugboard class that aggregates PlugLead objects
    """

    def __init__(self):
        self.plug_leads: List[PlugLead] = []
        self.plugs_in_use: List[str] = []

    def add(self, plug_lead):
        """
        Method that adds a PlugLead object to Plugboard
        :param plug_lead: PlugLead object
        :return: void
        """
        if self.plugs_connected() == 0:
            self.plug_leads.append(plug_lead)
            self.plugs_in_use.extend(plug_lead.get_mapping())
        elif self.plugs_connected() < 10:
            if not any(plug in self.plugs_in_use for plug in plug_lead.get_mapping()):
                self.plug_leads.append(plug_lead)
                self.plugs_in_use.extend(plug_lead.get_mapping())
        else:
            raise NoPlugsAvailableException('All leads have been connected')

    def encode(self, character):
        """
        Method that encodes PlugLeads
        :param character: character to be encoded
        :return: encoded character
        """
        for a_lead in self.plug_leads:
            if character in a_lead.get_mapping():
                return a_lead.encode(character)
        return character

    def get_plugs_settings(self):
        """
        Method that returns plugs settings
        :return: list of plug pairs
        """
        connections = []
        for connection in self.plug_leads:
            connections.append(str(connection))
        return connections

    def plugs_connected(self):
        """
        Helper method that returns the number of currently connected plugs
        :return: number of connected plugs
        """
        return len(self.plug_leads)


class Rotor:
    """
    Class that models a single rotor
    """

    def __init__(self, rotor_type, initial_position, ring_setting):

        # notch position
        self.notch: int = RotorData.notch[rotor_type.lower()]
        # type of rotor
        self.rotor_type: str = rotor_type
        # helper variable for aligning rotor's labels with wiring
        self.rotor_offset: int = 1
        # equivalent of wiring pattern
        self.rotor_wiring: List[str] = list(RotorData.sequence[rotor_type.lower()])

        # sequence of 26 alphabet letters from A to Z
        self.label: List[str] = list(RotorData.sequence['alpha'])

        # initial rotor position
        self.initial_position: str = initial_position
        # initial ring setting
        self.ring_setting: int = ring_setting

        self.set_rotor_to_initial_position(initial_position)
        self.set_rotor_ring_setting(ring_setting)

    def encode_right_to_left(self, character):
        """
        Method that encodes a character simulating current flow from right to left
        :param character: a character to encode
        :return: encoded character
        """
        return self.rotor_wiring[self.label.index(character)]

    def encode_left_to_right(self, character):
        """
        Method that encodes a character simulating current flow from left to right
        :param character: a character to encode
        :return: encoded character
        """
        return self.label[self.rotor_wiring.index(character)]

    def rotate_rotor(self, direction=-1):
        """
        Method that simulates rotor rotation
        :param direction: rotation direction
        :return: void
        """
        rotation = deque(self.rotor_wiring)
        rotation.rotate(direction)
        self.rotor_wiring = rotation
        offset_rotation = deque(self.label)
        offset_rotation.rotate(direction)
        self.label = offset_rotation

    def get_initial_position(self):
        """
        Getter method for initial_position
        :return: initial_position
        """
        return self.initial_position

    def set_rotor_to_initial_position(self, initial_position):
        """
        Method that sets rotor to required initial position
        :param initial_position: rotor's initial position
        :return: void
        """
        for number_of_rotations in range(self.label.index(initial_position)):
            rotation = deque(self.rotor_wiring)
            rotation.rotate(-1)
            self.rotor_wiring = rotation
            offset_rotation = deque(self.label)
            offset_rotation.rotate(-1)
            self.label = offset_rotation
            self.set_rotor_offset(1)

    def set_rotor_ring_setting(self, ring_setting):
        """
        Method that sets initial rotor's ring setting
        :param ring_setting:
        :return: void
        """
        for number_of_rotation in range(ring_setting - 1):
            rotation = deque(self.rotor_wiring)
            rotation.rotate()
            self.rotor_wiring = rotation
            offset_rotation = deque(self.label)
            offset_rotation.rotate()
            self.label = offset_rotation
            self.set_rotor_offset(-1)
            self.adjust_notch_position()

    def get_ring_setting(self):
        """
        Getter method for ring_setting
        :return: ring_setting
        """
        return self.ring_setting

    def set_rotor_offset(self, direction):
        """
        Method that adjusts label position to wiring
        :param direction: direction of rotation
        :return: void
        """
        self.rotor_offset += direction
        if self.rotor_offset <= 1:
            self.rotor_offset = 26
        if self.rotor_offset >= 27:
            self.rotor_offset = 1

    def adjust_notch_position(self):
        """
        Method that adjusts notch position so it is always relative to label and wiring
        :return: void
        """
        if type(self.notch) is int:
            self.notch -= 1
            if self.notch < 1:
                self.notch = 26

    def reset_deque(self):
        """
        Helper method that resets deque data type
        :return: void
        """
        self.notch = RotorData.notch[self.rotor_type.lower()]
        self.rotor_offset = 1
        self.rotor_wiring.clear()
        self.label.clear()
        self.rotor_wiring = list(RotorData.sequence[self.rotor_type.lower()])
        self.label = list(RotorData.sequence['alpha'])
        self.set_rotor_to_initial_position(self.initial_position)
        self.set_rotor_ring_setting(self.ring_setting)

    def __str__(self):
        """
        :return: Textual representation of Rotor object
        """
        return f"Type: {self.rotor_type}, Initial position: {self.initial_position}, Ring setting {self.ring_setting}"


class Reflector:
    """
    Class that models a reflector
    """

    def __init__(self, reflector_type, wiring=None):
        self.reflector_sequence: List[str] = list(RotorData.sequence[reflector_type.lower()])
        self.label: List[str] = list(RotorData.sequence['alpha'])
        self.r_type: str = reflector_type

        self.wiring: List[PlugLead] = []
        self.connected_wires = []

        if wiring is None:
            self.wire_reflector(self.get_wiring_pairs())
        else:
            self.wire_reflector(wiring)

    def encode(self, character):
        """
           Method that encodes a character in reflector
           :param character: character to encode
           :return: encode character
           """
        for a_lead in self.wiring:
            if character in a_lead.get_mapping():
                return self.label.index(a_lead.encode(character))
        return character

    def get_wiring_pairs(self):
        """
        Method that produces wiring pairs
        :return: a list of wiring pairs
        """
        wiring = []
        for i in range(len(self.label) - 1):
            if not any(self.label[i] in l for l in wiring):
                wiring.append(self.label[i] + self.reflector_sequence[i])
        return wiring

    def add(self, plug_lead):
        """
        Method that adds a wiring pair to reflector
        :param plug_lead:
        :return: void
        """
        if len(self.wiring) == 0:
            self.wiring.append(plug_lead)
            self.connected_wires.extend(plug_lead.get_mapping())
        else:
            if not any(plug in self.connected_wires for plug in plug_lead.get_mapping()):
                self.wiring.append(plug_lead)
                self.connected_wires.extend(plug_lead.get_mapping())

    def wire_reflector(self, wiring):
        """
        Method that constructs wiring for a reflector
        :param wiring:
        :return: void
        """
        for wire in wiring:
            self.add(PlugLead(wire))

    def get_wiring(self):
        """
        Method that obtains reflector wiring pairs
        :return: list of wiring pairs
        """
        connections = []
        for connection in self.wiring:
            connections.append(str(connection))
        return connections


class RotorData:
    """
    Helper static class with rotors and reflectors wiring and notch positions
    """

    sequence = {
        'alpha': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'beta': 'LEYJVCNIXWPBQMDRTAKZGFUHOS',
        'gamma': 'FSOKANUERHMBTIYCWLQPZXVGJD',
        'i': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ',
        'ii': 'AJDKSIRUXBLHWTMCQGZNPYFVOE',
        'iii': 'BDFHJLCPRTXVZNYEIWGAKMUSQO',
        'iv': 'ESOVPZJAYQUIRHXLNFTGKDCMWB',
        'v': 'VZBRGITYUPSDNHLXAWMJQOFECK',
        'a': 'EJMZALYXVBWFCRQUONTSPIKHGD',
        'b': 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
        'c': 'FVPJIAOYEDRZXWGCTKUQSBNMHL',
    }

    notch = {
        'i': 17,  # Q
        'ii': 5,  # E
        'iii': 22,  # V
        'iv': 10,  # J
        'v': 26,  # Z
        'beta': False,  # no notch
        'gamma': False,  # no notch
    }


class NoPlugsAvailableException(Exception):
    pass


class ConnectionExistsException(Exception):
    pass


class EnigmaDrumFull(Exception):
    pass


class MissingRotors(Exception):
    pass


if __name__ == "__main__":

    enigma = Enigma()
    plugboard = Plugboard()

    enigma.set_plugboard(plugboard)

    enigma.add_rotor(Rotor('IV', 'Z', 19))
    enigma.add_rotor(Rotor('III', 'V', 15))
    enigma.add_rotor(Rotor('II', 'E', 11))
    enigma.add_rotor(Rotor('I', 'Q', 7))
    enigma.set_reflector(Reflector('C'))

    print(enigma.encode_sequence('Z'))

