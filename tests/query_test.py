from litmon import PubMedInterface


def test_single_query():

    # run query
    pmi = PubMedInterface(
        fname=None,
        query='aging',
        start_date='2020/01/01',
        end_date='2020/01/01',
    )
    df = pmi._single_query('2020/02/12')

    # check mostly filled out
    assert((df['title'] == '').mean() < 0.05)
    assert((df['abstract'] == '').mean() < 0.05)

    # check many articles
    assert(df.shape[0] > 100)


if __name__ == '__main__':
    test_single_query()
