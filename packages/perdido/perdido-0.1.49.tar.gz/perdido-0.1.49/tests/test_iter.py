
class Test:

    def __init__(self):
        self.tokens = ['a', 'b', 'c']


    def __iter__(self):
        for t in self.tokens:
            yield t

    def __len__(self):
        return len(self.tokens)

if __name__ == '__main__':
    print('test')
    p = Test()

    print(len(p))

    for t in p:
        print(t)