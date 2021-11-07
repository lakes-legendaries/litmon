from litmon import PubMedQuerier


def test():

    # run query
    querier = PubMedQuerier(
        email='mike@lakeslegendaries.com',
        tool='org.mfoundation.litmon',
        max_results=30,
    )
    results = querier.query('(cancer) AND (2020/01/01 [edat])')

    # check results
    assert(results.shape[0] == 30)
    assert(querier.count == 30)

    # check running count
    querier.query('(cancer) AND (2020/01/02 [edat])')
    assert(querier.count == 60)


if __name__ == '__main__':
    test()
