from os import remove

from litmon import PubMedIDExtractor


def test():
    ifname = 'tests/dump.mbox'
    ofname = 'tests/pmid.txt'
    line = 'sdsagbPMID: 12345678\nasdgsaewq PMID87654321 PMID7 PMI44444444'
    try:
        with open(ifname, 'w') as file:
            print(line, file=file)
        PubMedIDExtractor(
            mbox_fname=[ifname],
            pmids_fname=ofname,
        )
        pmids = open(ofname).read().splitlines()
        assert(len(pmids) == 2)
        assert(pmids[0] == '12345678')
        assert(pmids[1] == '87654321')
    finally:
        remove(ifname)
        remove(ofname)


if __name__ == '__main__':
    test()
