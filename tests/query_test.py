from litmon import PubMedQuerier


def test():

    # run query
    querier = PubMedQuerier(max_results=30)
    results, dates = querier.query('(cancer) AND (2020/01/01 [edat])')

    # check results
    assert(results.shape[0] == 30)
    assert(dates.shape[0] == 30)
    assert(all([d.year == 2020 for d in dates]))
    assert(all([d.month == 1 for d in dates]))
    assert(all([d.day == 1 for d in dates]))
    assert(querier._count == 30)

    # check running count
    results, dates = querier.query('(cancer) AND (2020/01/02 [edat])')
    assert(querier._count == 60)


if __name__ == '__main__':
    test()
