'''
Simulation of cryptographic encoding and decoding of strings
'''

import random
import crypto_utils as cu

FIRST = 65
ALPHLEN = 26


class Cypher():
    '''
    Super class for all the different different cyphers
    '''
    def __init__(self):
        '''
        Initialize the alphabet to a the list [0, 1, ..., ALPHLEN-1].
        '''
        self.alphabet = list(range(ALPHLEN))

    def decode(self, text, key):
        '''
        Decode <text> using <key>
        '''

    def encode(self, text, key):
        '''
        Encode <text> using <key>
        '''

    def verify(self, clear_text, key):
        '''
        Verify that the encryption and then decryption of <text> using <key>
        result in the same string.
        '''
        return self.decode(self.encode(clear_text, key), key) == clear_text

    def indexes_to_text(self, ord_list):
        '''
        Translate a list of numbers to characters. FIRST is the ordinal of the
        character in the alphabet, i.e. FIRST=65 means the first char is 'A'
        '''
        return "".join([chr(FIRST + i) for i in ord_list])


class Ceasar(Cypher):
    '''
    This cypher encodes each character by adding a number
    '''

    def decode(self, text, key):
        '''
        Decoding a ceasar cypher with the key value <key> is the same as
        encoding using the key -<key>
        '''
        return self.encode(text, -key)

    def encode(self, text, key):
        '''
        For each charachter in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then add <key> and wrap around by using the mod
        of the length of the alphabet (<ALPHLEN>).
        '''
        enc = [(ord(c) - FIRST + key) % ALPHLEN for c in text]
        return self.indexes_to_text(enc)


class Multiplication(Cypher):
    '''
    This cypher encodes each character by multiplying it by a number
    '''

    def decode(self, text, key):
        '''
        For each char in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then multiply the modular inverse of the key
        and wrap around using mod of the length of tha alphabet (<ALPHLEN>).
        '''
        dec = [((ord(c) - FIRST) * cu.modular_inverse(key, ALPHLEN)) % ALPHLEN
               for c in text]
        return self.indexes_to_text(dec)

    def encode(self, text, key):
        '''
        For each char in <text>, find it's index in our alphabet
        (ord(c) - FIRST), then multiply by <key> and wrap around using the
        mod of the length of tha alphabet (<ALPHLEN>).
        '''
        enc = [((ord(c) - FIRST) * key) % ALPHLEN for c in text]
        return self.indexes_to_text(enc)


class Affine(Cypher):
    '''
    This cypher combines the Multiplication- and Ceasar-cypher.
    '''
    def __init__(self):
        self.ceasar = Ceasar()
        self.multi = Multiplication()
        super().__init__()

    def decode(self, text, key):
        '''
        <key> is a tuple (n, m) where n is the key for the
        Multiplication-cypher, and m is is the key for the Ceasar-cypher.
        First decode the Ceasar-cypher using n, then decode the result of that
        with the Multiplication-cypher using m
        '''
        c_dec = self.ceasar.decode(text, key[1])
        decoded = self.multi.decode(c_dec, key[0])
        return decoded

    def encode(self, text, key):
        '''
        <key> is a tuple (n, m) where n is the key for the
        Multiplication-cypher, and m is is the key for the Ceasar-cypher.
        '''
        multi_enc = self.multi.encode(text, key[0])
        encoded = self.ceasar.encode(multi_enc, key[1])
        return encoded


class Unbreakable(Cypher):
    '''
    This cypher encodes a string using another string as the ke
    '''

    def decode(self, text, key):
        '''
        To decode <text> we find the "inverse" of <key>, and encode using this
        inverted key.
        '''
        dec_key = self.indexes_to_text(
            [(ALPHLEN - (ord(c) - FIRST) % ALPHLEN) % ALPHLEN for c in key])
        return self.encode(text, dec_key)

    def encode(self, text, key):
        '''
        To encode <text> we first repeat the string in <key> enough times to be
        the same length as <text>. Then we encrypt by adding the value of each
        char in <text> with the corresponding char in the repeated key.
        '''
        rep_key = "".join([key[i % len(key)] for i in range(len(text))])
        enc = [(ord(c) + ord(k) - 2*FIRST) %
               ALPHLEN for c, k in zip(text, rep_key)]
        return self.indexes_to_text(enc)


class RSA(Cypher):
    '''
    Prime numbers are sick bro!
    '''

    def decode(self, text, key):
        pass

    def encode(self, text, key):
        pass


class Person():
    '''
    Super class for sending/recieving ciphers.
    '''
    def __init__(self, cypher):
        self.key = None
        self.cypher = cypher

    def set_key(self, key):
        '''
        Set the cypher key
        '''
        self.key = key

    def get_key(self):
        '''
        Get the cypher key
        '''
        return self.key

    def operate_cypher(self, text):
        '''
        Cypher <text>
        '''


class Sender(Person):
    '''
    Class for creation of a cypher
    '''

    def operate_cypher(self, text):
        return self.cypher.encode(text, self.key)


class Reciever(Person):
    '''
    Class for decyphering
    '''

    def operate_cypher(self, text):
        return self.cypher.decode(text, self.key)

    def generate_keys(self, bits=12):
        '''
        Generate an RSA-key
        '''
        p = cu.generate_random_prime(bits)
        q = cu.generate_random_prime(bits)
        while p == q:
            q = cu.generate_random_prime(bits)

        n = p * q
        phi = (p-1)*(q-1)

        e = random.randint(2, phi)
        d = cu.modular_inverse(e, phi)

        self.key = (n, d)
        return (n, e)


def main():

    c = Ceasar()
    m = Multiplication()
    a = Affine()
    u = Unbreakable()
    text = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

    print("Ceasar:  ", c.verify(text, 2))
    print("Multi:   ", m.verify(text, 3))
    print("Affine:  ", a.verify(text, (3, 2)))
    print("Unbreak: ", u.verify(text, "PIZZA"))

    text = "HEMMELIGHET"
    print(text)
    enc = u.encode(text, "PIZZA")
    print(enc)
    dec = u.decode(enc, "PIZZA")
    print(dec)

    # u = Unbreakable()
    # text = "HEI"
    # key = "PIZZA"
    # print(key)
    # u.decode(text, key)


if __name__ == '__main__':
    main()
