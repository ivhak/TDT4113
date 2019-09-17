import crypto as c
import random


def test_hacker(tests, test_words):
    for word in test_words:
        for test in tests:
            h = c.Hacker(test[1])
            enc = test[1].encode(word, test[2])
            dec = h.operate_cypher(enc)
            assert word in dec, f'Hacking of {test[1]}-cypher of "{word}" fail'


def test_cyphers(tests, test_words):
    for test in tests:
        for word in test_words:
            verify = test[1].verify(word, test[2])
            assert verify, f'{test[0]} failed with input "{word}"'


def test_rsa():
    r = c.Reciever(c.RSA())
    key = r.generate_keys(bits=8)
    s = c.Sender(c.RSA())
    s.set_key(key)

    text = 'KODE'
    enc = s.operate_cypher(text)
    dec = r.operate_cypher(enc)
    assert dec == text, f'RSA decrypt failed. Should be "{text}", was "{dec}"'


def main():
    with open('src/english_words.txt', 'r') as word_file:
        words = {line.rstrip('\n') for line in word_file}
    random_words = [random.sample(words, 1)[0] for i in range(5)]

    tests = [
        ('Caesar', c.Caesar(), random.randint(1, c.ALPHLEN-1)),
        ('Multiplication', c.Multiplication(), 3),
        ('Affine', c.Affine(), (3, 2)),
        ('Unbreakable', c.Unbreakable(), random.choice(random_words)),
    ]

    test_cyphers(tests, random_words)
    test_hacker(tests, random_words)
    test_rsa()


if __name__ == '__main__':
    main()
