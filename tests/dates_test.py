from litmon import drange


def test():
    drng = drange('2013/11-2014/02')
    assert(len(drng) == 4)
    assert(drng[0] == (2013, 11))
    assert(drng[1] == (2013, 12))
    assert(drng[2] == (2014, 1))
    assert(drng[3] == (2014, 2))


if __name__ == '__main__':
    test()
