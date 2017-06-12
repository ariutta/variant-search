import server
import unittest


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()

    # def tearDown(self):

    def test_show_suggestions(self):
        response = self.app.get('/suggestions?gene=OA')
        assert b'["OAS1", "OASL", "OAT"]' == response.data

    def test_show_variants_one(self):
        response = self.app.get('/variants?gene=BRAP')
        assert b'[{"Gene": "BRAP", "Nucleotide Change": "", "Protein Change": "", "Alias": "", "Region": "", "Reported Classification": "Uncertain significance", "Last Evaluated": "2016-01-20", "Last Updated": "2017-04-25", "More Info": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000240600"}]' == response.data

if __name__ == '__main__':
    unittest.main()
