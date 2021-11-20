from litmon import DBaseBuilder


def test():
    drange = DBaseBuilder.drange('2013/11-2014/02')
    assert(len(drange) == 4)
    assert(drange[0] == (2013, 11))
    assert(drange[1] == (2013, 12))
    assert(drange[2] == (2014, 1))
    assert(drange[3] == (2014, 2))


if __name__ == '__main__':
    test()
