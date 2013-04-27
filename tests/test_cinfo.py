import unittest

from test_simobj import VectCalc


class TestVectCalcCInfo(unittest.TestCase):

    def member_names(self, **kwds):
        return list(VectCalc.cinfo.member_names(**kwds))

    def test_cinfo_member_names_by_empty_kwds(self):
        self.assertEqual(
            self.member_names(),
            ['num_i', 'v1', 'v2', 'v3', 'ans'])

    def test_cinfo_member_names_by_cdt(self):
        self.assertEqual(
            self.member_names(cdt='int'),
            ['num_i', 'v1', 'v2', 'v3', 'ans'])

    def test_cinfo_member_names_by_ndim(self):
        self.assertEqual(
            self.member_names(ndim=0),
            ['num_i', 'ans'])
        self.assertEqual(
            self.member_names(ndim=1),
            ['v1', 'v2', 'v3'])

    def test_cinfo_indices(self):
        self.assertEqual(VectCalc.cinfo.indices, set(['i']))
