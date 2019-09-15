'''
Simulation of cryptographic encoding and decoding of strings
'''

import random
import crypto_utils as cu

FIRST = 97
ALPHLEN = 26


class Cypher():
    '''
    Super class for all the different cyphers
    '''
    def __init__(self):
        '''
        Initialize the alphabet to the list [0, 1, ..., ALPHLEN-1].
        '''
        self.alphabet = list(range(ALPHLEN))

    def decode(self, text: str, key) -> str:
        ''' Decode <text> using <key> '''

    def encode(self, text: str, key) -> str:
        ''' Encode <text> using <key> '''

    def verify(self, clear_text: str, key) -> bool:
        '''
        Verify that the encryption and then decryption of <text> using <key>
        result in the same string.
        '''
        return self.decode(self.encode(clear_text, key), key) == clear_text

    def translate_to_text(self, ord_list: [int]) -> str:
        '''
        Translate a list of numbers to characters. FIRST is the ordinal of the
        character in the alphabet, i.e. FIRST=65 means the first char is 'A'
        '''
        return "".join([chr(FIRST + i) for i in ord_list])


class Caesar(Cypher):
    '''
    This cypher encodes each character by adding a number
    '''
    def decode(self, text: str, key: int) -> str:
        '''
        Decoding a ceasar cypher with the key value <key> is the same as
        encoding using the key -<key>
        '''
        return self.encode(text, -key)

    def encode(self, text: str, key: int) -> str:
        '''
        For each charachter in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then add <key> and wrap around by using the mod
        of the length of the alphabet (<ALPHLEN>).
        '''
        enc = [(ord(c) - FIRST + key) % ALPHLEN for c in text]
        return self.translate_to_text(enc)


class Multiplication(Cypher):
    '''
    This cypher encodes each character by multiplying it by a number
    '''
    def decode(self, text: str, key: int) -> str:
        '''
        For each char in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then multiply the modular inverse of the key
        and wrap around using mod of the length of tha alphabet (<ALPHLEN>).
        '''
        dec = [((ord(c) - FIRST) * cu.modular_inverse(key, ALPHLEN)) % ALPHLEN
               for c in text]
        return self.translate_to_text(dec)

    def encode(self, text: str, key: int) -> str:
        '''
        For each char in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then multiply by <key> and wrap around using the
        mod of the length of the alphabet (<ALPHLEN>).
        '''
        enc = [((ord(c) - FIRST) * key) % ALPHLEN for c in text]
        return self.translate_to_text(enc)


class Affine(Cypher):
    '''
    This cypher combines the Multiplication- and Caesar-cypher.
    '''
    def __init__(self):
        self.ceasar = Caesar()
        self.multi = Multiplication()
        super().__init__()

    def decode(self, text: str, key: tuple) -> str:
        '''
        <key> is a tuple (n, m) where n is the key for the
        Multiplication-cypher, and m is is the key for the Caesar-cypher.
        First decode the Caesar-cypher using n, then decode the result of that
        with the Multiplication-cypher using m
        '''
        c_dec = self.ceasar.decode(text, key[1])
        decoded = self.multi.decode(c_dec, key[0])
        return decoded

    def encode(self, text: str, key: tuple) -> str:
        '''
        <key> is a tuple (n, m) where n is the key for the
        Multiplication-cypher, and m is is the key for the Caesar-cypher.
        '''
        multi_enc = self.multi.encode(text, key[0])
        encoded = self.ceasar.encode(multi_enc, key[1])
        return encoded


class Unbreakable(Cypher):
    '''
    This cypher encodes a string using another string as the key
    '''
    def decode(self, text: str, key: str) -> str:
        '''
        To decode <text> we find the "inverse" of <key>, and encode using this
        inverted key.
        '''
        dec_key = self.translate_to_text(
            [(ALPHLEN - (ord(c) - FIRST) % ALPHLEN) % ALPHLEN for c in key])

        return self.encode(text, dec_key)

    def encode(self, text: str, key: str) -> str:
        '''
        To encode <text> we first repeat the string in <key> enough times to be
        the same length as <text>. Then we encrypt by adding the value of each
        char in <text> with the corresponding char in the repeated key.
        '''

        # Repeat the key until it is the same length as <text>
        rep_key = "".join([key[i % len(key)] for i in range(len(text))])

        # The ordinal of each char in text gets added with the ordinal of the
        # corresponding char in the repeated key. FIRST get subtracted from
        # each to get the right indexes in our alphabet
        enc = [(ord(c) - FIRST + ord(k) - FIRST) % ALPHLEN
               for c, k in zip(text, rep_key)]

        return self.translate_to_text(enc)


class RSA(Cypher):
    '''
    Prime numbers are sick bro!
    '''
    def decode(self, text, key):
        n = key[0]
        d = key[1]
        dec_blocks = [pow(c, d, n) for c in text]
        return cu.text_from_blocks(dec_blocks, 1)

    def encode(self, text, key):
        t = cu.blocks_from_text(text, 1)
        n = key[0]
        e = key[1]
        enc_blocks = [pow(b, e, n) for b in t]
        return enc_blocks


class Person():
    '''
    Super class for sending/recieving cyphers.
    '''
    def __init__(self, cypher):
        self.key = None
        self.cypher = cypher

    def set_key(self, key):
        ''' Set the cypher key '''
        self.key = key

    def get_key(self):
        ''' Get the cypher key '''
        return self.key

    def operate_cypher(self, text: str) -> str:
        ''' Cypher <text> '''


class Sender(Person):
    '''
    Class for creation of a cypher
    '''
    def operate_cypher(self, text: str) -> str:
        return self.cypher.encode(text, self.key)


class Reciever(Person):
    '''
    Class for decyphering
    '''
    def operate_cypher(self, text: str) -> str:
        return self.cypher.decode(text, self.key)

    def generate_keys(self, bits=128):
        '''
        Generate an RSA-key
        '''
        p = cu.generate_random_prime(bits)
        q = cu.generate_random_prime(bits)
        while p == q:
            q = cu.generate_random_prime(bits)

        n = p * q
        phi = (p-1)*(q-1)

        e = random.randint(3, phi-1)
        d = cu.modular_inverse(e, phi)

        self.key = (n, d)
        return (n, e)


class Hacker(Reciever):
    '''
    Class for hacking of a cypher
    '''
    def __init__(self, cypher):
        super().__init__(cypher)
        self.words = None

    def load_words(self, file='src/english_words.txt'):
        '''
        Load words from a file containing one word per line.
        '''
        with open(file, 'r') as word_file:
            self.words = {line.rstrip('\n') for line in word_file}

    def operate_cypher(self, text: str) -> str:
        '''
        Bruteforce decode cypher
        '''
        self.load_words()
        matches = []

        def check_match(decode, matches=matches, words=self.words):
            if decode in words:
                matches += [decode]

        # Caesar/Multiplication
        if isinstance(self.cypher, (Caesar, Multiplication)):
            for i in range(ALPHLEN):
                check_match(self.cypher.decode(text, i))

        # Affine
        if isinstance(self.cypher, Affine):
            for i in range(ALPHLEN):
                for j in range(ALPHLEN):
                    check_match(self.cypher.decode(text, (i, j)))

        # Unbreakable
        if isinstance(self.cypher, Unbreakable):
            for word in self.words:
                check_match(self.cypher.decode(text, word))

        return matches


def main():

    c = Caesar()
    m = Multiplication()
    a = Affine()
    u = Unbreakable()
    text = "nourishment"
    enc_c = c.encode(text, 16)
    enc_m = m.encode(text, 9)
    enc_a = a.encode(text, (3, 2))
    enc_u = u.encode(text, "hello")

    h_c = Hacker(Caesar())
    h_m = Hacker(Multiplication())
    h_a = Hacker(Affine())
    h_u = Hacker(Unbreakable())

    print("Caesar:", h_c.operate_cypher(enc_c))
    print("Multiplication:", h_m.operate_cypher(enc_m))
    print("Affine:", h_a.operate_cypher(enc_a))
    print("Unbreakable:", h_u.operate_cypher(enc_u))


if __name__ == '__main__':
    main()
