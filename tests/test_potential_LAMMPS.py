from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestFAQ():

    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        action = potentials.load_record('Action')

        assert action.style == 'Action'
        assert action.modelroot == 'action'
        assert action.date == date.today()
        assert action.type is None
        assert len(action.potentials) == 0
        assert action.comment is None

    def test_assign_init(self):
        """Test value assignment during init"""
        
        action = potentials.load_record('Action', date='2019-09-12',
                                        type='retraction', comment='boo boo')
    
        assert action.date == date(2019, 9, 12)
        assert action.type == 'retraction'
        assert len(action.potentials) == 0
        assert action.comment == 'boo boo'

        jsonmodel = '{"action": {"date": "2019-09-12", "type": "retraction", "comment": "boo boo"}}'

        assert action.build_model().json() == jsonmodel
        assert action.model.json() == jsonmodel

        meta = action.metadata()
        assert meta['name'] == '2019-09-12 boo boo'
        assert meta['date'] == date(2019, 9, 12)
        assert meta['type'] == 'retraction'
        assert meta['potentials'] == []
        assert meta['comment'] == 'boo boo'

    def test_assign(self):
        """Test value assignment after init"""
        action = potentials.load_record('Action')

        action.date = '2019-09-12'
        action.type = 'retraction'
        action.comment = 'boo boo'
        assert action.date == date(2019, 9, 12)
        assert action.type == 'retraction'
        assert action.comment == 'boo boo'
        
        with pytest.raises(ValueError):
            action.type = 'unsupported'

    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('Action/*.json'):
            action = potentials.load_record('Action', model=fname)
            with open(fname) as f:
                content = f.read()
            print(action.build_model().json(indent=4))
            print(content)
            assert action.build_model().json(indent=4) == content

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        actions, df = potdb.get_actions(return_df=True, refresh_cache=True)
        assert len(actions) == 3

        actions = potdb.get_records('Action', date='2099-10-23')
        assert len(actions) == 1

        actions = potdb.get_records('Action', type=['site change', 'new posting'])
        assert len(actions) == 2

        actions = potdb.get_records('Action', potential_key='3837b6da-05c4-4148-97cd-90b26a2092df')
        assert len(actions) == 1

        actions = potdb.get_records('Action', potential_id='2009--Purja-Pun-G-P-Mishin-Y--Ni-Al')
        assert len(actions) == 1

        actions = potdb.get_records('Action', dois='10.1080/14786430903258184')
        assert len(actions) == 1

        actions = potdb.get_records('Action', elements='Cu')
        assert len(actions) == 1

        actions = potdb.get_records('Action', fictionalelements='Ni')
        assert len(actions) == 1

        actions = potdb.get_records('Action', othername='NiAl3')
        assert len(actions) == 1

        actions = potdb.get_records('Action', comment='example')
        assert len(actions) == 3


    def test_add_potential(self):
        action = potentials.load_record('Action')
        action.add_potential(potential_key='asdf', potential_id='ppppp', dois=['asdf', '525'], elements='B', fictionalelements='Po', othername='Rob')

        jsonstr = '{"potential-info": {"key": "asdf", "id": "ppppp", "doi": ["asdf", "525"], "fictional-element": "Po", "element": "B", "other-element": "Rob"}}'

        assert action.potentials[0].build_model().json() == jsonstr

    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_record('Action', potential_id='2009--Purja-Pun-G-P-Mishin-Y--Ni-Al')

        with pytest.raises(ValueError):
            potdb.get_record('Action', comment='example', prompt=False)

        with pytest.raises(ValueError):
            potdb.get_record('Action', comment='nnosasfddoij')


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
        
        action = potentials.load_record('Action', name='dbtesting', date='1212-12-12',
                                        type='site change', comment='test record for database operations')


        potdb.save_action(action)
        potdb.get_action(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_action(action=action)
            potdb.get_action(name='dbtesting', local=False)

        potdb.delete_action(action=action, 
                            remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_action(name='dbtesting')

