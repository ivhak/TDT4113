import crypto_utils as cu
import sys


class Cypher():
    def __init__(self):
        self.alphabet = list(range(65, 65+25+1))  # ord('A'), ..., ord('̃~')

    def decode(self, text):
        pass

    def encode(self, text):
        pass

    def verify(self, clear_text):
        return self.decode(self.encode(clear_text)) == clear_text

    def get_alphabet(self):
        return [chr(x) for x in self.alphabet]


class Ceasar(Cypher):
    def __init__(self):
        super().__init__()

    def decode(self, text, key):
        s = self.alphabet[0]
        enc = [s + (ord(c) - s - key) % len(self.alphabet) for c in text]
        return "".join([chr(n) for n in enc])

    def encode(self, text, key):
        s = self.alphabet[0]
        enc = [s + (ord(c) - s + key) % len(self.alphabet) for c in text]
        return "".join([chr(n) for n in enc])


class Multiplication(Cypher):
    def __init__(self):
        super().__init__()

    def decode(self, text, key):
        s = self.alphabet[0]
        a_len = len(self.alphabet)

        enc = [s + (ord(c) - s) * cu.modular_inverse(key, a_len) % a_len
               for c in text]

        return "".join([chr(n) for n in enc])

    def encode(self, text, key):
        s = self.alphabet[0]
        a_len = len(self.alphabet)

        enc = [s + ((ord(c) - s) * key) % a_len for c in text]

        return "".join([chr(n) for n in enc])


class Affine(Cypher):
    def __init__(self):
        self.ceasar = Ceasar()
        self.multi = Multiplication()
        super().__init__()

    def decode(self, text, key):
        c_dec = self.ceasar.decode(text, key[1])
        decoded = self.multi.decode(c_dec, key[0])
        return decoded

    def encode(self, text, key):
        multi_enc = self.multi.encode(text, key[0])
        encoded = self.ceasar.encode(multi_enc, key[1])
        return encoded


class Unbreakable(Cypher):
    def __init__(self):
        super().__init__()

    def decode(self, text, key):
        s = self.alphabet[0]
        a_len = len(self.alphabet)

        # TODO
        decrypt_key = [chr(s + (a_len - ord(c) % a_len)) for c in key]
        print(decrypt_key)

    def encode(self, text, key):
        s = self.alphabet[0]
        a_len = len(self.alphabet)
        repeated_key = "".join([key[i % len(key)] for i in range(len(text))])
        print(repeated_key)

        return "".join([chr(s + ((ord(c) - s) + (ord(k) - s)) % a_len)
                        for c, k in zip(text, repeated_key)])


class Person():
    def __init__(self, cypher):
        self.key = None
        self.cypher = cypher

    def set_key(self, key):
        self.key = key

    def get_key(self):
        return self.key

    def operate_cipher(self, text):
        pass


class Sender(Person):
    def __init__(self, cypher):
        super().__init__(cypher)

    def operate_cipher(self, text):
        return self.cypher.encode(text, self.key)


class Reciever(Person):
    def __init__(self, cypher):
        super().__init__(cypher)

    def operate_cipher(self, text):
        return self.cypher.decode(text, self.key)


def main():
    c = Unbreakable()

    s = Sender(c)
    s.set_key("PIZZA")

    s = Reciever(c)
    s.set_key("PIZZA")

    text = "HEMMELIGHET"

    print(text)
    crypt = s.operate_cipher(text)
    print(crypt)
    decrypt = s.operate_cipher(crypt)
    print(decrypt)


if __name__ == '__main__':
    main()
