from litmon import PubMedIDExtractor


def test():
    data = ['sdsagbPMID: 12345678\nasdgsaewq PMID87654321 PMID7 PMI44444444']
    extractor = PubMedIDExtractor(data)
    assert(len(extractor.pmids) == 2)
    assert(extractor.pmids[0] == '12345678')
    assert(extractor.pmids[1] == '87654321')


if __name__ == '__main__':
    test()
