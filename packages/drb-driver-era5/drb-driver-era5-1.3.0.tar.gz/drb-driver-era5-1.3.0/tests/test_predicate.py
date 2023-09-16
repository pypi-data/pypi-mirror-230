import unittest

from drb.exceptions.core import DrbException

from drb.drivers.era5 import Era5PredicateEra5PressureLevelByHour, \
    Era5PredicateEra5PressureLevelsByMonth, \
    Era5PredicateEra5LandMonthly, Era5PredicateEra5Land, \
    Era5PredicateEra5SingleLevelsByMonth


class TestEra5NodePredicate(unittest.TestCase):

    def test_get_item_predicatePressure(self):

        predicate = Era5PredicateEra5PressureLevelByHour(
            year=1959,
            month=1,
            day=1,
            time=0,
            pressure_level=2,
            variable='surface_pressure')

        self.assertEqual(predicate.to_dict()['variable'], 'surface_pressure')

        self.assertEqual(predicate.to_dict()['pressure_level'], 2)

        predicate = Era5PredicateEra5PressureLevelByHour(
            year=1959,
            month=3,
            day=1,
            time=0,
            variable='surface_pressure')

        self.assertEqual(predicate.to_dict()['variable'], 'surface_pressure')
        self.assertEqual(predicate.to_dict()['month'], 3)

        self.assertEqual(predicate.to_dict()['product_type'], 'reanalysis')

        self.assertFalse(predicate.matches(None))

    def test_get_item_predicatePressureMonthly(self):

        predicate = Era5PredicateEra5PressureLevelsByMonth(
            year=1959,
            month=1,
            day=1,
            time=0,
            pressure_level=3,
            variable='divergence')

        self.assertEqual(predicate.to_dict()['variable'], 'divergence')

        self.assertEqual(predicate.to_dict()['pressure_level'], 3)

    def test_get_item_predicateLandMonthly(self):

        predicate = Era5PredicateEra5LandMonthly(
            year=1959,
            month=1,
            variable='surface_pressure')

        self.assertEqual(predicate.to_dict()['variable'], 'surface_pressure')

        self.assertEqual(predicate.to_dict()['month'], 1)
        self.assertEqual(predicate.to_dict()['time'], 0)

        self.assertNotIn('day', predicate.to_dict().keys())

    def test_get_item_predicateLand(self):

        predicate = Era5PredicateEra5Land(
            year=1959,
            month=1,
            time=23,
            day=2,
            variable='surface_pressure')

        self.assertEqual(predicate.to_dict()['variable'], 'surface_pressure')

        self.assertEqual(predicate.to_dict()['month'], 1)
        self.assertEqual(predicate.to_dict()['time'], 23)
        self.assertEqual(predicate.to_dict()['day'], 2)

    def test_get_item_predicateLandSingleLevelsByMonth(self):

        predicate = Era5PredicateEra5SingleLevelsByMonth(
            year=1959,
            month=1,
            time=0,
            variable='mean_wave_direction',
            prodcuct_type='monthly_averaged_ensemble_members')

        self.assertEqual(predicate.to_dict()['variable'],
                         'mean_wave_direction')
        self.assertNotIn('day', predicate.to_dict().keys())

        self.assertEqual(predicate.to_dict()['time'], 0)

        with self.assertRaises(DrbException):
            Era5PredicateEra5SingleLevelsByMonth(
                year=1959,
                month=1,
                time=[1, 2, 3],
                variable='mean_wave_direction',
                prodcuct_type='monthly_averaged_ensemble_members')

        predicate = Era5PredicateEra5SingleLevelsByMonth(
            year=1959,
            month=1,
            time=[1, 2, 3],
            variable='mean_wave_direction',
            product_type='monthly_averaged_ensemble_members_by_hour_of_day')

        self.assertEqual(predicate.to_dict()['variable'],
                         'mean_wave_direction')
        self.assertNotIn('day', predicate.to_dict().keys())

        self.assertEqual(predicate.to_dict()['time'], [1, 2, 3])
