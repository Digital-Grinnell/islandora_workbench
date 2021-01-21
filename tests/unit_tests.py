"""unittest tests that do not require a live Drupal.
"""

import sys
import os
from ruamel.yaml import YAML
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import workbench_utils


class TestCompareStings(unittest.TestCase):

    def test_strings_match(self):
        res = workbench_utils.compare_strings('foo', 'foo  ')
        self.assertTrue(res)
        res = workbench_utils.compare_strings('foo', 'Foo')
        self.assertTrue(res)
        res = workbench_utils.compare_strings('foo', 'Foo#~^.')
        self.assertTrue(res)
        res = workbench_utils.compare_strings('foo bar baz', 'foo   bar baz')
        self.assertTrue(res)

    def test_strings_do_not_match(self):
        res = workbench_utils.compare_strings('foo', 'foot')
        self.assertFalse(res)


class TestSplitGeolocationString(unittest.TestCase):

    def test_split_geolocation_string_single(self):
        config = {'subdelimiter': '|'}
        res = workbench_utils.split_geolocation_string(
            config, '49.16667, -123.93333')
        self.assertDictEqual(res[0], {'lat': '49.16667', 'lng': '-123.93333'})

    def test_split_geolocation_string_multiple(self):
        config = {'subdelimiter': '|'}
        res = workbench_utils.split_geolocation_string(
            config, '30.16667, -120.93333|50.1,-120.5')
        self.assertDictEqual(res[0], {'lat': '30.16667', 'lng': '-120.93333'})
        self.assertDictEqual(res[1], {'lat': '50.1', 'lng': '-120.5'})

    def test_split_geolocation_string_multiple_at_sign(self):
        config = {'subdelimiter': '@'}
        res = workbench_utils.split_geolocation_string(
            config, '49.16667, -123.93333@50.1,-120.5')
        self.assertDictEqual(res[0], {'lat': '49.16667', 'lng': '-123.93333'})
        self.assertDictEqual(res[1], {'lat': '50.1', 'lng': '-120.5'})

    def test_split_geolocation_string_with_leading_slash(self):
        config = {'subdelimiter': '@'}
        res = workbench_utils.split_geolocation_string(
            config, r'\+49.16667, -123.93333@\+50.1,-120.5')
        self.assertDictEqual(res[0], {'lat': '+49.16667', 'lng': '-123.93333'})
        self.assertDictEqual(res[1], {'lat': '+50.1', 'lng': '-120.5'})


class TestSplitTypedRelationString(unittest.TestCase):

    def test_split_typed_relation_string_single(self):
        config = {'subdelimiter': '|'}
        res = workbench_utils.split_typed_relation_string(
            config, 'relators:pht:5', 'foo')
        self.assertDictEqual(res[0],
                             {'target_id': int(5),
                              'rel_type': 'relators:pht',
                              'target_type': 'foo'})

    def test_split_typed_relation_string_multiple(self):
        config = {'subdelimiter': '|'}
        res = workbench_utils.split_typed_relation_string(
            config, 'relators:pht:5|relators:con:10', 'bar')
        self.assertDictEqual(res[0],
                             {'target_id': int(5),
                              'rel_type': 'relators:pht',
                              'target_type': 'bar'})
        self.assertDictEqual(res[1],
                             {'target_id': int(10),
                              'rel_type': 'relators:con',
                              'target_type': 'bar'})

    def test_split_typed_relation_string_multiple_at_sign(self):
        config = {'subdelimiter': '@'}
        res = workbench_utils.split_typed_relation_string(
            config, 'relators:pht:5@relators:con:10', 'baz')
        self.assertDictEqual(res[0],
                             {'target_id': int(5),
                              'rel_type': 'relators:pht',
                              'target_type': 'baz'})
        self.assertDictEqual(res[1],
                             {'target_id': int(10),
                              'rel_type': 'relators:con',
                              'target_type': 'baz'})


class TestValidateLanguageCode(unittest.TestCase):

    def test_validate_code_in_list(self):
        res = workbench_utils.validate_language_code('es')
        self.assertTrue(res)

    def test_validate_code_not_in_list(self):
        res = workbench_utils.validate_language_code('foo')
        self.assertFalse(res)


class TestValidateLatlongValue(unittest.TestCase):

    def test_validate_good_latlong_values(self):
        values = ['+90.0, -127.554334', '90.0, -127.554334', '-90,-180', '+50.25,-117.8', '+48.43333,-123.36667']
        for value in values:
            res = workbench_utils.validate_latlong_value(value)
            self.assertTrue(res)

    def test_validate_bad_latlong_values(self):
        values = ['+90.1 -100.111', '045, 180', '+5025,-117.8', '-123.36667']
        for value in values:
            res = workbench_utils.validate_latlong_value(value)
            self.assertFalse(res)


class TestValidateNodeCreatedDateValue(unittest.TestCase):

    def test_validate_good_date_string_values(self):
        values = ['2020-11-15T23:49:22+00:00']
        for value in values:
            res = workbench_utils.validate_node_created_date_string(value)
            self.assertTrue(res)

    def test_validate_bad_date_string_values(self):
        values = ['2020-11-15:23:49:22+00:00', '2020-11-15T:23:49:22', '2020-11-15']
        for value in values:
            res = workbench_utils.validate_node_created_date_string(value)
            self.assertFalse(res)


class TestValideCalendarDate(unittest.TestCase):

    def test_validate_good_edtf_values(self):
        good_values = ['190',
                       '1900',
                       '2020-10',
                       '2021-10-12'
                       ]
        for good_value in good_values:
            res = workbench_utils.validate_calendar_date(good_value)
            self.assertTrue(res, good_value)

    def test_validate_bad_edtf_values(self):
        bad_values = ['1900-05-45',
                      '1900-13-01',
                      '1900-02-31',
                      ]
        for bad_value in bad_values:
            res = workbench_utils.validate_calendar_date(bad_value)
            self.assertFalse(res, bad_value)


class TestSetMediaType(unittest.TestCase):

    def setUp(self):
        yaml = YAML()
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Media types are mapped from extensions.
        types_config_file_path = os.path.join(
            dir_path, 'assets', 'set_media_type_test', 'multi_types_config.yml')
        with open(types_config_file_path, 'r') as f:
            multi_types_config_file_contents = f.read()
        self.multi_types_config_yaml = yaml.load(
            multi_types_config_file_contents)

        # Media type is set for all media.
        type_config_file_path = os.path.join(
            dir_path,
            'assets',
            'set_media_type_test',
            'single_type_config.yml')
        with open(type_config_file_path, 'r') as f:
            single_type_config_file_contents = f.read()
        self.single_type_config_yaml = yaml.load(
            single_type_config_file_contents)

    def test_multi_types_set_media_type(self):
        res = workbench_utils.set_media_type(
            '/tmp/foo.txt', self.multi_types_config_yaml)
        self.assertEqual(res, 'extracted_text')

        res = workbench_utils.set_media_type(
            '/tmp/foo.tif', self.multi_types_config_yaml)
        self.assertEqual(res, 'file')

        res = workbench_utils.set_media_type(
            '/tmp/foo.mp4', self.multi_types_config_yaml)
        self.assertEqual(res, 'video')

        res = workbench_utils.set_media_type(
            '/tmp/foo.png', self.multi_types_config_yaml)
        self.assertEqual(res, 'image')

        res = workbench_utils.set_media_type(
            '/tmp/foo.pptx', self.multi_types_config_yaml)
        self.assertEqual(res, 'document')

        res = workbench_utils.set_media_type(
            '/tmp/foo.xxx', self.multi_types_config_yaml)
        self.assertEqual(res, 'file')

    def test_single_type_set_media_type(self):
        res = workbench_utils.set_media_type(
            '/tmp/foo.bar', self.single_type_config_yaml)
        self.assertEqual(res, 'barmediatype')


class TestGetCsvFromExcel(unittest.TestCase):
    """Note: this tests the extraction of CSV data from Excel only,
       not using and Excel file as an input CSV file.
    """
    def setUp(self):
        self.config = {'input_dir': 'tests/assets/excel_test',
                       'input_csv': 'test_excel_file.xlsx',
                       'excel_worksheet': 'Sheet1',
                       'excel_csv_filename': 'excel_csv.csv',
                       'id_field': 'id'
                       }

        self.csv_file_path = os.path.join(self.config['input_dir'], self.config['excel_csv_filename'])

    def test_get_csv_from_excel(self):
        workbench_utils.get_csv_from_excel(self.config)
        csv_data_fh = open(self.csv_file_path, "r")
        csv_data = csv_data_fh.readlines()
        csv_data_fh.close()

        self.assertEqual(len(csv_data), 5)

        fourth_row = csv_data[4]
        fourth_row_parts = fourth_row.split(',')
        self.assertEqual(fourth_row_parts[1], 'Title 4')

        # @todo: Test CSV field templates.

    def tearDown(self):
        os.remove(self.csv_file_path)


if __name__ == '__main__':
    unittest.main()
