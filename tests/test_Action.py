from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestAction():
    
    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        record = potentials.load_record('Action')

        assert record.style == 'Action'
        assert record.modelroot == 'action'
        assert record.date == date.today()
        assert record.type is None
        assert len(record.potentials) == 0
        assert record.comment is None

    def test_assign_init(self):
        """Test value assignment during init"""

        record = potentials.load_record('Action', date='2019-09-12',
                                        type='retraction', comment='boo boo')
    
        assert record.date == date(2019, 9, 12)
        assert record.type == 'retraction'
        assert len(record.potentials) == 0
        assert record.comment == 'boo boo'

        jsonmodel = '{"action": {"date": "2019-09-12", "type": "retraction", "comment": "boo boo"}}'

        assert record.build_model().json() == jsonmodel
        assert record.model.json() == jsonmodel

        meta = record.metadata()
        assert meta['name'] == '2019-09-12 boo boo'
        assert meta['date'] == date(2019, 9, 12)
        assert meta['type'] == 'retraction'
        assert meta['potentials'] == []
        assert meta['comment'] == 'boo boo'

    def test_assign(self):
        """Test value assignment after init"""
        record = potentials.load_record('Action')

        record.date = '2019-09-12'
        record.type = 'retraction'
        record.comment = 'boo boo'
        assert record.date == date(2019, 9, 12)
        assert record.type == 'retraction'
        assert record.comment == 'boo boo'
        
        with pytest.raises(ValueError):
            record.type = 'unsupported'

    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('Action/*.json'):
            record = potentials.load_record('Action', model=fname)
            with open(fname) as f:
                content = f.read()
            print(record.build_model().json(indent=4))
            print(content)
            assert record.build_model().json(indent=4) == content

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        records, df = potdb.get_actions(return_df=True, refresh_cache=True)
        assert len(records) == 3

        records = potdb.get_actions(date='2099-10-23')
        assert len(records) == 1

        records = potdb.get_actions(type=['site change', 'new posting'])
        assert len(records) == 2

        records = potdb.get_actions(potential_key='3837b6da-05c4-4148-97cd-90b26a2092df')
        assert len(records) == 1

        records = potdb.get_actions(potential_id='2009--Purja-Pun-G-P-Mishin-Y--Ni-Al')
        assert len(records) == 1

        records = potdb.get_actions(dois='10.1080/14786430903258184')
        assert len(records) == 1

        records = potdb.get_actions(elements='Cu')
        assert len(records) == 1

        records = potdb.get_actions(fictionalelements='Ni')
        assert len(records) == 1

        records = potdb.get_actions(othername='NiAl3')
        assert len(records) == 1

        records = potdb.get_actions(comment='example')
        assert len(records) == 3


    def test_add_potential(self):
        record = potentials.load_record('Action')
        record.add_potential(potential_key='asdf', potential_id='ppppp', dois=['asdf', '525'], elements='B', fictionalelements='Po', othername='Rob')

        jsonstr = '{"potential-info": {"key": "asdf", "id": "ppppp", "doi": ["asdf", "525"], "fictional-element": "Po", "element": "B", "other-element": "Rob"}}'

        assert record.potentials[0].build_model().json() == jsonstr

    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_action(potential_id='2009--Purja-Pun-G-P-Mishin-Y--Ni-Al')

        with pytest.raises(ValueError):
            potdb.get_action(comment='example', prompt=False)

        with pytest.raises(ValueError):
            potdb.get_action(comment='nnosasfddoij')


    def test_retrieve(self, tmp_path):
        """Test retrieving and saving a single record from the database"""
        potdb = self.potdb

        potdb.retrieve_action(dest=tmp_path, type='site change')

    def test_download(self, tmp_path):
        """Test downloading records from the remote and saving to the local"""
        if test_with_remote:
            potdb = potentials.Database(localpath=tmp_path, remote=True)
            potdb.download_actions()

    def test_save_upload_delete(self):
        """Test saving, uploading and deleting a record"""
        potdb = self.potdb
        
        record = potentials.load_record('Action', name='dbtesting', date='1212-12-12',
                                        type='site change', comment='test record for database operations')


        potdb.save_action(record)
        potdb.get_action(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_action(action=record)
            potdb.get_action(name='dbtesting', local=False)

        potdb.delete_action(action=record, 
                            remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_action(name='dbtesting')

