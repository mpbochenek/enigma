from enigma import *
from itertools import product
from itertools import combinations
from itertools import permutations


class CodeBreaker:
    """
    Class for breaking codes from the assignment
    """

    def __init__(self, data):
        self.missing_information = self.set_missing_information(data)
        self.code = data['code']
        self.crib = data['crib']
        self.enigma = Enigma()
        self.data = data
        self.setup_starting_rotors()
        self.setup_starting_position()
        self.setup_ring_setting()
        self.plugboard = self.setup_plugboard(data)
        self.reflector = self.setup_reflector(data)
        self.rotors = self.setup_rotors(data)
        self.setup_enigma()

        self.reflectors = ['a', 'b', 'c']
        self.starting_positions = self.get_possible_starting_positions()
        self.r3_combinations = self.get_r3_combination()
        if 'plugboard' in self.missing_information:
            self.plug_combinations = self.get_plugs_combinations()
        self.reflector_combinations = []

    def set_missing_information(self, data):
        """
        Method that checks which Enigma settings are missing
        :param data: JSON input data with settings
        :return: missing_info list
        """
        missing_info = []
        for element in data:
            if data[element] is None:
                missing_info.append(element)
            elif element == 'plugboard':
                for plug in data[element]:
                    if len(plug) < 2:
                        missing_info.append({'plug': plug})
                        missing_info.append('plugboard')

        return missing_info

    def setup_rotors(self, rotor_info):
        """
        Set Enigma rotors in required position
        :param rotor_info: initial rotor settings and type
        :return: list of rotors
        """
        rotors = []
        rotors_control = []
        for i in range(len(rotor_info['rotors']) - 1, -1, -1):
            rotors.append(Rotor(rotor_info['rotors'][i], rotor_info['starting_positions'][i],
                                int(rotor_info['ring_settings'][i])))
        return rotors

    def setup_plugboard(self, data):
        """
        Set Enigma plugboard
        :param data: initial plugboard setting
        :return: plugboard
        """
        plugboard = Plugboard()
        if 'plugboard' not in self.missing_information:
            for plug in data['plugboard']:
                plugboard.add(PlugLead(plug))
        return plugboard

    def setup_reflector(self, data):
        """
        Set Enigma reflector
        :data: reflector setting
        :return: reflector
        """
        if 'reflector' not in self.missing_information:
            return Reflector(data['reflector'])
        return Reflector('b')

    def change_reflector(self, new_reflector):
        """
        Change Enigma reflector
        :new_reflector: new Enigma reflector
        :return: void
        """
        self.reflector = new_reflector

    def setup_enigma(self):
        """
        Apply initial Enigma settings
        :return: void
        """
        self.enigma = Enigma()
        self.enigma.set_plugboard(self.plugboard)
        new_rotors = self.setup_rotors(self.data)
        for rotor in new_rotors:
            self.enigma.add_rotor(rotor)
        self.enigma.set_reflector(self.reflector)

    def setup_starting_position(self):
        """
        Set rotors' starting position
        :return: void
        """
        if 'starting_positions' in self.missing_information:
            self.data['starting_positions'] = ['A', 'A', 'A']

    def setup_ring_setting(self):
        """
        Set rotor's ring settings
        :return: void
        """
        if 'ring_settings' in self.missing_information:
            self.data['ring_settings'] = ['01', '01', '01']

    def setup_starting_rotors(self):
        """
        Set starting rotors' types
        :return: void
        """
        if 'rotors' in self.missing_information:
            self.data['rotors'] = ['I', 'II', 'III']

    def change_starting_position(self, new_position):
        """
        Change rotors' starting position
        :return: void
        """
        self.data['starting_positions'] = new_position

    def change_rotors(self, new_setup):
        """
        Change Enigma rotors
        :return: void
        """
        self.data['rotors'] = new_setup

    def change_ring_setting(self, new_settings):
        """
        Change Enigma ring setting
        :return: void
        """
        self.data['ring_settings'] = new_settings

    def get_possible_starting_positions(self):
        """
        Get a list of possible starting positions
        :return: list of possible starting positions
        """
        possible_positions = product('ABCDEFGHIJKLMNOPQRSTUVWXYZ', repeat=3)
        possible_positions_list = [list(el) for el in possible_positions]
        return possible_positions_list

    def get_r3_combination(self):
        ring_settings = ['02', '04', '06', '08', '20', '22', '24', '26']
        possible_ring_settings = product(ring_settings, repeat=3)
        possible_ring_settings_list = [list(el) for el in possible_ring_settings]
        possible_rotors = product(['II', 'IV', 'Beta', 'Gamma'], repeat=3)
        possible_rotors_list = [list(el) for el in possible_rotors]
        a_list = [possible_ring_settings_list, possible_rotors_list, self.reflectors]
        combination = [p for p in product(*a_list)]
        return combination

    def get_plugs_combinations(self):
        """
        Get a list of possible plug combinations
        :return: a list of possible plug combinations
        """
        all_plugs = ''
        for plug in self.data['plugboard']:
            all_plugs += plug
        all_plugs = list(all_plugs)
        all_plugs = set(all_plugs)
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letters = list(letters)
        letters = set(letters)
        not_used_letters = list(all_plugs.symmetric_difference(letters))

        partial_plugs = {}
        for plug in self.missing_information:
            if type(plug) == dict:
                partial_plugs[plug['plug']] = []

        for key in partial_plugs:
            a_list = [not_used_letters, key]
            partial_plugs[key] = list(product(*a_list))

        for key in partial_plugs:
            partial_plugs[key] = [''.join(v) for v in partial_plugs[key]]

        partial_plugs_keys = list(partial_plugs.keys())
        expression_string = '['
        for el in partial_plugs_keys:
            expression_string += 'partial_plugs[\'' + el + '\'],'
        expression_string = expression_string[:-1]
        expression_string += ']'
        expression = eval(expression_string)
        plugs_combinations = list(product(*expression))

        return plugs_combinations

    def change_plugboard(self, new_plugs):
        """
        Change plugboard setting
        :new_plugs: new plugboard setting
        :return: void
        """
        current_plugs = []
        for plug in self.data['plugboard']:
            if len(plug) > 1:
                current_plugs.append(plug)
        current_plugs.extend(new_plugs)
        new_plugboard = Plugboard()
        for plug in current_plugs:
            new_plugboard.add(PlugLead(plug))
        self.plugboard = new_plugboard

    def set_reflector_combinations(self, reflector):
        """
        Set new reflector combinations
        :reflector: reflector type
        :return: void
        """
        wiring = reflector.get_wiring_pairs()
        possible_wiring_changes = list(combinations(wiring, 4))

        all_combinations = []
        more_combinations = []
        for pwc in possible_wiring_changes:
            more_combinations.append(list(combinations(pwc, 2)))
        for combination in more_combinations:
            tmp = [combination[0] + combination[5], combination[1] + combination[4], combination[2] + combination[3]]
            all_combinations.append(tmp)

        wiring_io = []
        for pwc in possible_wiring_changes:
            input = []
            output = []
            for el in pwc:
                input.append(el[0])
                output.append(el[1])
            wiring_io.append([input, output])

        wiring_io_permutations = []
        for i in wiring_io:
            wiring_io_permutations.append([list(''.join(x) for x in zip(each_permutation, i[1])) for each_permutation in
                                           permutations(i[0], len(i[1]))])

        for i in wiring_io_permutations:
            for j in i:
                self.reflector_combinations.append(j)

    def rewire_reflector(self, reflector, new_wiring):
        """
        Rewire Enigma reflector
        :reflector: Enigma reflector
        :new_wiring: new reflector wiring
        :return: rewired reflector
        """
        pairs = reflector.get_wiring_pairs()
        new = new_wiring
        used = []
        for i in new_wiring:
            used.extend(list(i))
        for i in range(len(pairs)):
            if not any(el in list(used) for el in list(pairs[i])):
                new.append(pairs[i])
                used.extend(list(pairs[i]))

        return new

    def encode(self):
        """
        Encodes assignment code 1, 2 and 4
        :return: encoded message and missing settings
        """
        not_found = True
        i = 0
        result = ''
        sp = self.data['starting_positions']
        while not_found:
            cypher = self.enigma.encode_sequence(self.code)

            if self.crib in cypher:
                not_found = False
                result = f"Message: {cypher} \nReflector: {self.reflector.r_type} " \
                         f"\nInitial positions: {sp}"

                result += f"\nPlugs settings: {self.plugboard.get_plugs_settings()}"
            else:
                if 'reflector' in self.missing_information:
                    if i > 2:
                        break
                    self.change_reflector(Reflector(self.reflectors[i]))
                    self.setup_enigma()
                elif 'starting_positions' in self.missing_information:
                    self.change_starting_position(self.starting_positions[i])
                    sp = self.starting_positions[i]
                    self.setup_enigma()
                elif 'plugboard' in self.missing_information:
                    new_plugs = []
                    if self.plug_combinations:
                        plug = self.plug_combinations.pop()
                        new_plugs.append(plug[0])
                        new_plugs.append(plug[1])
                    else:
                        break
                    self.change_plugboard(new_plugs)
                    self.setup_enigma()
            i += 1
        return result

    def encode_part3(self):
        """
        Encodes assignment code 3
        :return: encoded message and missing settings
        """
        not_found = True
        i = 0
        while not_found:
            cypher = self.enigma.encode_sequence(self.code)
            # print(cypher)
            if self.crib in cypher:
                not_found = False
                result = f"Message: {cypher} \nReflector: {self.reflector.r_type} " \
                         f"\nRotors: {self.r3_combinations[i - 1][1]} \nRing settings: {self.r3_combinations[i - 1][0]}"
                result += f"\nPlugs settings: {self.plugboard.get_plugs_settings()}"
            else:
                self.change_rotors(self.r3_combinations[i][1])
                self.change_ring_setting(self.r3_combinations[i][0])
                self.change_reflector(Reflector(self.r3_combinations[i][2]))
                self.setup_enigma()

            i += 1
            if i > len(self.r3_combinations):
                result = 'Crib not found'
                break
        return result

    def encode_part5(self):
        """
        Encodes assignment code 5
        :return: encoded message and missing settings
        """
        not_found = True
        i = 0
        self.set_reflector_combinations(self.reflector)
        while not_found:
            cypher = self.enigma.encode_sequence(self.code)

            crib = [
                'FACEBOOK',
                'FLICKER',
                'LINKEDIN',
                'TWITTER',
                'INSTAGRAM',
                'YOUTUBE',
                'PINTEREST',
                'TUMBLR',
                'REDDIT',
                'SNAPCHAT',
            ]
            for cr in crib:
                if cr in cypher:
                    not_found = False
                    result = f"Message: {cypher} \nReflector type: {self.reflector.r_type} \nReflector wiring: {self.reflector.get_wiring()}"

            new_reflector = Reflector(self.reflector.r_type,
                                      self.rewire_reflector(self.reflector, self.reflector_combinations[i]))

            self.change_reflector(new_reflector)
            self.setup_enigma()

            i += 1
            if i >= len(self.reflector_combinations):
                result = 'No results'
                break
        return result

    def get_code(self):
        return self.code


if __name__ == "__main__":
    code1 = {
        'code': 'DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ',
        'crib': 'SECRETS',
        'rotors': [
            'Beta',
            'Gamma',
            'V'
        ],
        'reflector': 'c',
        'ring_settings': [
            '04',
            '02',
            '14'
        ],
        'starting_positions': [
            'M',
            'J',
            'M'
        ],
        'plugboard': [
            'KI',
            'XN',
            'FL'
        ]
    }

    code2 = {
        'code': 'CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH',
        'crib': 'UNIVERSITY',
        'rotors': [
            'Beta',
            'I',
            'III'
        ],
        'reflector': 'B',
        'ring_settings': [
            '23',
            '02',
            '10'
        ],
        'starting_positions': None,
        'plugboard': [
            'VH',
            'PT',
            'ZG',
            'BJ',
            'EY',
            'FS'
        ]
    }

    code3 = {
        'code': 'ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY',
        'crib': 'THOUSAND',
        'rotors': None,
        'reflector': None,
        'ring_settings': None,
        'starting_positions': [
            'E',
            'M',
            'Y'
        ],
        'plugboard': [
            'FH',
            'TS',
            'UQ',
            'BE',
            'KD',
            'AL'
        ]
    }

    code4 = {
        'code': 'SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW',
        'crib': 'DURINGTHE',
        'rotors': ['V', 'III', 'IV'],
        'reflector': 'a',
        'ring_settings': ['24', '12', '10'],
        'starting_positions': [
            'S',
            'W',
            'U'
        ],
        'plugboard': [
            'WP',
            'RJ',
            'VF',
            'HN',
            'CG',
            'BS',
            'A',
            'I',
        ]
    }

    code5 = {
        'code': 'HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX',
        'crib': 'UNKNOWN',
        'rotors': ['V', 'II', 'IV'],
        'reflector': 'b',
        'ring_settings': ['06', '18', '07'],
        'starting_positions': [
            'A',
            'J',
            'L'
        ],
        'plugboard': [
            'UG',
            'IE',
            'PO',
            'NX',
            'WT',

        ]
    }