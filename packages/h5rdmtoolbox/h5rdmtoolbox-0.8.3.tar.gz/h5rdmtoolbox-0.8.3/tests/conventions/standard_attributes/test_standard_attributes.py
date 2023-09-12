"""Testing the standard attributes"""
import inspect
import pint
import re
import unittest
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Union

import h5rdmtoolbox as h5tbx
from h5rdmtoolbox import __author_orcid__
from h5rdmtoolbox import tutorial
from h5rdmtoolbox.conventions import Convention
from h5rdmtoolbox.conventions.consts import DefaultValue
from h5rdmtoolbox.conventions.errors import StandardAttributeError
from h5rdmtoolbox.conventions.standard_attributes import StandardAttribute


class TestStandardAttributes(unittest.TestCase):

    @staticmethod
    def assertPintUnitEqual(unit1: [str, pint.Unit], unit2: Union[str, pint.Unit]):
        """Assert that two units are equal by converting them to pint.Unit"""
        assert pint.Unit(unit1) == pint.Unit(unit2)

    def setUp(self) -> None:
        self.connected = h5tbx.utils.has_internet_connection()

    def assert_standard_attribute(self, sa):
        self.assertIsInstance(sa.name, str)
        self.assertIsInstance(sa.description, str)
        self.assertIsInstance(sa.is_positional(), bool)
        self.assertIsInstance(sa.target_method, str)
        self.assertIsInstance(sa.validator, h5tbx.conventions.standard_attributes.StandardAttributeValidator)

    def test_standard_attribute_basics(self):
        test = StandardAttribute('test',
                                 validator={'$type': 'string'},
                                 target_method='create_dataset',
                                 description='A test',
                                 )
        self.assertEqual('test', test.name)
        self.assertEqual('A test.', test.description)
        self.assertEqual(True, test.is_positional())
        self.assertEqual('create_dataset', test.target_method)
        self.assertEqual(None, test.alternative_standard_attribute)
        self.assert_standard_attribute(test)

    def test_datetime(self):
        datetime_attr = StandardAttribute(
            name='datetime',
            validator='$datetime',
            target_method="__init__",
            description='Timestamp of data recording start',
            default_value='$NONE',
        )
        cv = Convention('test_datetime', contact=__author_orcid__)
        cv.add(datetime_attr)
        cv.register()
        h5tbx.use(cv.name)
        with h5tbx.File() as h5:
            dt = datetime.now()
            h5.datetime = dt
            self.assertEqual(h5.datetime, datetime.fromisoformat(dt.isoformat()))

        import h5py
        fname = h5tbx.utils.generate_temporary_filename()
        with h5py.File(fname, 'w') as h5:
            h5.attrs['datetime'] = '20230830'

        with h5tbx.File(fname) as h5:
            self.assertEqual('20230830', h5.datetime)

    def test_data_source(self):
        h5tbx.use(None)
        data_source = StandardAttribute('data_source',
                                        validator={'$in': ['simulation', 'experiment']},
                                        target_method='create_dataset',
                                        description='Data source',
                                        default_value='simulation'
                                        )
        self.assertEqual(data_source.name, 'data_source')
        self.assertEqual(data_source.description, 'Data source.')
        self.assertEqual(False, data_source.is_positional())
        self.assertEqual(data_source.target_method, 'create_dataset')
        self.assertEqual(data_source.default_value, 'simulation')
        self.assert_standard_attribute(data_source)

        cv = h5tbx.conventions.Convention('test_convention', contact=__author_orcid__)
        cv.add(data_source)
        cv.register()
        h5tbx.use(cv.name)
        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, data_source='simulation')
            self.assertEqual(h5['test'].attrs['data_source'], 'simulation')
            self.assertEqual(h5['test'].data_source, 'simulation')
            with self.assertRaises(StandardAttributeError):
                h5.create_dataset('test2', data=1, data_source='invalid')
            h5.create_dataset('test2', data=1)
            self.assertEqual(h5['test2'].attrs['data_source'], 'simulation')
            self.assertEqual(h5['test2'].data_source, 'simulation')

        # pass as attrs instead of keyword argument
        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, attrs=dict(data_source='experiment'))
            self.assertEqual(h5['test'].attrs.raw['data_source'], 'experiment')

    def test_add_with_requirements(self):
        h5tbx.use(None)
        comment_name = StandardAttribute('comment',
                                         validator={'$minlength': 10},
                                         target_method='create_dataset',
                                         alternative_standard_attribute='long_name',
                                         description='A comment',
                                         requirements='long_name'
                                         )

        long_name_convention = h5tbx.conventions.Convention('long_name_convention_with_requirements',
                                                            contact=__author_orcid__)
        with self.assertRaises(h5tbx.errors.ConventionError):
            long_name_convention.add(comment_name)
            long_name_convention.register()

    def test_initialization_of_StandardAttribute(self):
        h5tbx.use(None)
        with self.assertRaises(ValueError):
            # providing an invalid method
            StandardAttribute('long_name',
                              validator={'$regex': r'^[a-zA-Z].*(?<!\s)$'},
                              target_method='invalid_method',
                              alternative_standard_attribute='comment',
                              description='A long name of a dataset',
                              )

        with self.assertRaises(ValueError):
            StandardAttribute('long_name',
                              validator={'$regex': r'^[a-zA-Z].*(?<!\s)$',
                                         '$regex2': r'^[a-zA-Z].*(?<!\s)$'},
                              target_method='__init__',
                              description='A long name of a file',
                              default_value='None'
                              )

        with self.assertRaises(TypeError):
            StandardAttribute('long_name',
                              validator={'$regex': r'^[a-zA-Z].*(?<!\s)$'},
                              target_method=3.4,
                              description='A long name of a file',
                              default_value='None'
                              )

        long_name = StandardAttribute('long_name',
                                      validator={'$regex': r'^[a-zA-Z].*(?<!\s)$'},
                                      target_method='__init__',
                                      description='A long name of a file',
                                      default_value='None'
                                      )
        self.assertEqual(None, long_name.default_value)

    def test_alternative_standard_attribute(self):
        h5tbx.use(None)
        long_name = StandardAttribute('long_name',
                                      validator={'$regex': r'^[a-zA-Z].*(?<!\s)$'},
                                      target_method='create_dataset',
                                      alternative_standard_attribute='comment',
                                      description='A long name of a dataset',
                                      )
        long_name_grp = StandardAttribute('long_name',
                                          validator={'$regex': r'^[a-zA-Z].*(?<!\s)$'},
                                          target_method='create_group',
                                          description='A long name of a group',
                                          default_value='$None'
                                          )
        comment_name = StandardAttribute('comment',
                                         validator={'$minlength': 10},
                                         target_method='create_dataset',
                                         alternative_standard_attribute='long_name',
                                         description='A comment',
                                         )

        long_name_convention = h5tbx.conventions.Convention('long_name_convention',
                                                            contact=__author_orcid__)
        long_name_convention.add(long_name)
        long_name_convention.add(comment_name)
        long_name_convention.add(long_name_grp)
        long_name_convention.register()
        h5tbx.use(long_name_convention.name)

        self.assertEqual(long_name.name, 'long_name')

        curr_convention = h5tbx.conventions.get_current_convention()
        self.assertEqual(curr_convention.name, 'long_name_convention')
        with self.assertRaises(h5tbx.conventions.errors.ConventionError):
            curr_convention.add(long_name)

        self.assertTrue('long_name' in inspect.signature(h5tbx.Group.create_dataset).parameters.keys())

        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, long_name='test')
            self.assertEqual(h5['test'].attrs['long_name'], 'test')

            with self.assertRaises(StandardAttributeError):
                h5.create_dataset('test2', data=1, long_name='123test')

        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, comment='A comment which is long enough')
            self.assertEqual(h5['test'].attrs['comment'], 'A comment which is long enough')
            with self.assertRaises(StandardAttributeError):
                h5.create_group('testgrp', long_name='123test')
            self.assertFalse('testgrp' in h5.keys())
            h5.create_group('testgrp', long_name='valid long name')
            self.assertTrue('testgrp' in h5.keys())
            self.assertEqual(h5['testgrp'].attrs['long_name'], 'valid long name')

        with self.assertRaises(StandardAttributeError):
            with h5tbx.File() as h5:
                h5.create_dataset('test', data=1)

        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, attrs=dict(long_name='test',
                                                         another_attr=3.4))
            self.assertEqual(h5['test'].attrs['long_name'], 'test')
            self.assertEqual(h5['test'].attrs['another_attr'], 3.4)

        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, comment='A comment which is long enough', long_name=None)
            self.assertEqual(h5['test'].attrs['comment'], 'A comment which is long enough')
            self.assertTrue('long_name' not in h5['test'].attrs.keys())

        with h5tbx.File() as h5:
            h5.create_dataset('test', data=1, comment='A comment which is long enough', attrs=dict(long_name=None))
            self.assertEqual(h5['test'].attrs['comment'], 'A comment which is long enough')
            self.assertTrue('long_name' not in h5['test'].attrs.keys())

    def test_references(self):
        bibtex_entry = {'article': {'journal': 'Nice Journal',
                                    'comments': 'A comment',
                                    'pages': '12--23',
                                    'month': 'jan',
                                    'abstract': 'This is an abstract. '
                                                'This line should be long enough to test\nmultilines...',
                                    'title': 'An amazing title',
                                    'year': '2013',
                                    'volume': '12',
                                    'ID': 'Cesar2013',
                                    'author': 'Jean Cesar',
                                    'keyword': 'keyword1, keyword2'}
                        }
        url = 'https://h5rdmtoolbox.readthedocs.io/en/latest/'

        bibtex_attrs = [StandardAttribute('bibtex',
                                          validator='$bibtex',
                                          target_method=tm,
                                          description='A reference to a publication in bibtext format',
                                          default_value='$None'
                                          ) for tm in ('create_dataset', 'create_group', '__init__')]

        url_attrs = [StandardAttribute('url',
                                       validator='$url',
                                       target_method=tm,
                                       description='A reference to an URL',
                                       default_value='$None'
                                       ) for tm in ('create_dataset', 'create_group', '__init__')]

        reference_attrs = [StandardAttribute('references',
                                             validator='$ref',
                                             target_method=tm,
                                             description='A reference to a publication in bibtext '
                                                         'format or an URL',
                                             default_value='$None'
                                             ) for tm in ('create_dataset', 'create_group', '__init__')]

        cv = Convention('test_references',
                        contact=__author_orcid__)
        for sattr in bibtex_attrs:
            cv.add(sattr)
        for sattr in url_attrs:
            cv.add(sattr)
        for sattr in reference_attrs:
            cv.add(sattr)

        cv.register()
        h5tbx.use(cv.name)

        for std_attr in ('url', 'bibtex', 'references'):
            self.assertTrue(std_attr in inspect.signature(h5tbx.Group.create_dataset).parameters.keys())
            self.assertTrue(std_attr in inspect.signature(h5tbx.Group.create_group).parameters.keys())
            self.assertTrue(std_attr in inspect.signature(h5tbx.File.__init__).parameters.keys())

        with h5tbx.File() as h5:
            if self.connected:
                h5.url = url
                self.assertEqual(h5.url, url)

                h5.bibtex = bibtex_entry
                self.assertTrue(h5.bibtex, dict)

                with self.assertRaises(StandardAttributeError):
                    h5.bibtex = {'invalid': {}}

            with self.assertRaises(StandardAttributeError):
                h5.url = 'invalid'

            h5.references = bibtex_entry
            self.assertDictEqual(h5.references, bibtex_entry)

            if self.connected:
                h5.references = url
                self.assertEqual(h5.references, url)

                h5.references = (bibtex_entry, url)
                self.assertEqual(h5.references[0], bibtex_entry)
                self.assertEqual(h5.references[1], url)

        from h5rdmtoolbox.conventions.references import validate_bibtex, validate_reference
        self.assertFalse(validate_reference('invalid'))
        with self.assertRaises(JSONDecodeError):
            self.assertFalse(validate_bibtex('invalid'))

        bibtex_entry = {'@article': {'journal': 'Nice Journal',
                                     'comments': 'A comment',
                                     'pages': '12--23',
                                     'month': 'jan',
                                     'abstract': 'This is an abstract. '
                                                 'This line should be long enough to test\nmultilines...',
                                     'title': 'An amazing title',
                                     'year': '2013',
                                     'volume': '12',
                                     'ID': 'Cesar2013',
                                     'author': 'Jean Cesar',
                                     'keyword': 'keyword1, keyword2'}
                        }
        self.assertTrue(validate_bibtex(bibtex_entry))
        self.assertTrue(validate_reference(bibtex_entry))

        bibtex_entry = {'invalid': {}}
        self.assertFalse(validate_bibtex(bibtex_entry))
        bibtex_entry = {'article': {}}
        self.assertFalse(validate_bibtex(bibtex_entry))

    def test_comment(self):

        class CommentValidator(h5tbx.conventions.standard_attributes.StandardAttributeValidator):

            keyword = 'comment'
            deprecated_keywords = ('$comment',)

            def __init__(self, ref=None, allow_None: bool = False):
                super().__init__(ref, allow_None)
                assert isinstance(ref[0], int) and ref[0] > 0
                assert isinstance(ref[1], int) and ref[1] > 0
                assert isinstance(ref[2], str)

            def __call__(self, value, parent=None, attrs=None):
                if len(value) < self.ref[0]:
                    raise ValueError('Comment is too short')
                if len(value) > self.ref[1]:
                    raise ValueError('Comment is too long')
                if not re.match(self.ref[2], value):
                    raise ValueError('Comment should start with a capital letter')
                return value

        n_validators = len(h5tbx.conventions.validators.get_validator())
        h5tbx.conventions.validators.register(CommentValidator)
        self.assertEqual(n_validators + 1, len(h5tbx.conventions.get_validator()))

        comment_file = StandardAttribute(
            name='comment-file',  # will strip "-file"
            validator={'$comment': (10, 101, r'^[A-Z].*$')},
            target_method="__init__",
            description='Additional information about the file'
        )

        comment_group = StandardAttribute(
            name='comment-group',
            validator={'$comment': (10, 101, r'^[A-Z].*$')},
            target_method="create_group",
            description='Additional information about the group'
        )

        comment_dataset = StandardAttribute(
            name='comment-dataset',
            validator={'$comment': (10, 101, r'^[A-Z].*$')},
            target_method="create_dataset",
            description='Additional information about the dataset'
        )
        cv = Convention('test_comment', contact=__author_orcid__)

        for sattr in (comment_file, comment_group, comment_dataset):
            self.assertTrue('-' not in sattr.name)
            cv.add(sattr)

        cv.register()

        h5tbx.use(cv.name)

        with h5tbx.File(comment='My comment is long enough') as h5:
            self.assertEqual(h5.comment, 'My comment is long enough')
            with self.assertRaises(StandardAttributeError):
                h5.comment = ' This is a comment, which starts with a space.'
            with self.assertRaises(StandardAttributeError):
                h5.comment = '9 This is a comment, which starts with a number.'
            with self.assertRaises(StandardAttributeError):
                h5.comment = 'Too short'
            with self.assertRaises(StandardAttributeError):
                h5.comment = 'Too long' * 100

            h5.comment = 'This comment is ok.'
            self.assertEqual(h5.comment, 'This comment is ok.')

    def test_units(self):
        """Test title attribute"""

        # units is required. thus default value is EMPTY
        units_attr = StandardAttribute('units',
                                       validator='$pintunit',
                                       target_method='create_dataset',
                                       description='A unit of a dataset')
        self.assertEqual(units_attr.default_value, DefaultValue.EMPTY)
        cv = h5tbx.conventions.Convention('ucv',
                                          contact=__author_orcid__)
        cv.add(units_attr)
        cv.register()
        h5tbx.use('ucv')

        with h5tbx.File() as h5:
            ds = h5.create_dataset('test',
                                   data=[1, 2, 3],
                                   units='m')
            with self.assertRaises(StandardAttributeError):
                ds.units = 'test'
            with self.assertRaises(StandardAttributeError):
                ds.units = ('test',)
            self.assertPintUnitEqual(ds.units, 'm')
            # creat pint unit object:
            ds.units = h5tbx.get_ureg().mm
            self.assertPintUnitEqual(ds.units, 'mm')
            with self.assertRaises(ValueError):
                del ds.units
            self.assertPintUnitEqual(ds.units, 'mm')

    def test_source(self):
        source_attrs = [StandardAttribute(
            name='data_base_source',
            validator={'$in': ('experimental',
                               'numerical',
                               'analytical',
                               'synthetically')},
            target_method=tm,
            description='Base source of data: experimental, numerical, '
                        'analytical or synthetically'
        ) for tm in ('__init__', 'create_dataset', 'create_group')]

        cv = Convention('source_convention',
                        contact=__author_orcid__)
        for sattr in source_attrs:
            cv.add(sattr)
        cv.register()

        h5tbx.use(cv.name)

        with h5tbx.File(data_base_source='experimental') as h5:
            with self.assertRaises(AttributeError):
                h5.base_source = 'numerical'
            with self.assertRaises(AttributeError):
                h5.base_source
            self.assertEqual(h5.data_base_source, 'experimental')
            h5.data_base_source = 'numerical'
            self.assertEqual(h5.data_base_source, 'numerical')
            with self.assertRaises(StandardAttributeError):
                h5.data_base_source = 'invalid'

    def test_from_yaml(self):
        if self.connected:
            convention_filename = tutorial.get_standard_attribute_yaml_filename()
            local_cv = h5tbx.conventions.Convention.from_yaml(convention_filename)
            local_cv.register()
            h5tbx.use(local_cv)

            with h5tbx.File(contact='https://orcid.org/0000-0001-8729-0482', data_type='numerical', mode='r+') as h5:
                h5.standard_name_table = 'https://zenodo.org/record/8266929'
