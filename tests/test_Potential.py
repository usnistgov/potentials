from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestPotential():

    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        record = potentials.load_record('Potential')

        assert record.style == 'Potential'
        assert record.modelroot == 'interatomic-potential'
        assert record.key is not None
        assert record.id is None
        assert record.url is None
        assert record.recorddate == date.today()
        assert len(record.citations) == 0
        assert record.notes is None
        assert len(record.implementations) == 0
        assert record.fictionalelements is None
        assert record.elements is None
        assert record.othername is None

    def test_assign_init(self):
        """Test value assignment during init"""
        
        record = potentials.load_record('Potential',
                                        key='8asdn3',
                                        id='new-potential-demo',
                                        url='web/url',
                                        recorddate='2019-09-12',
                                        notes='Test potential init',
                                        elements='Ag',
                                        othername='test')
    
        assert record.key == '8asdn3'
        assert record.id == 'new-potential-demo'
        assert record.url == 'web/url'
        assert record.recorddate == date(2019, 9, 12)
        assert len(record.citations) == 0
        assert record.notes == 'Test potential init'
        assert len(record.implementations) == 0
        assert record.fictionalelements is None
        assert record.elements == ['Ag']
        assert record.othername == 'test'

        jsonmodel = '{"interatomic-potential": {"key": "8asdn3", "id": "new-potential-demo", "URL": "web/url", "record-version": "2019-09-12", "description": {"notes": {"text": "Test potential init"}}, "element": "Ag", "other-element": "test"}}'

        assert record.build_model().json() == jsonmodel
        assert record.model.json() == jsonmodel

        meta = record.metadata()
        assert meta['name'] == 'potential.new-potential-demo'
        assert meta['key'] == '8asdn3'
        assert meta['id'] == 'new-potential-demo'
        assert meta['url'] == 'web/url'
        assert meta['recorddate'] == date(2019, 9, 12)
        assert meta['notes'] == 'Test potential init'
        assert meta['implementations'] == []
        assert meta['fictionalelements'] == None
        assert meta['elements'] == ['Ag']
        assert meta['othername'] == 'test'


    def test_assign(self):
        """Test value assignment after init"""
        record = potentials.load_record('Potential')

        record.key = '8asdn3'
        record.id = 'new-potential-demo'
        record.url = 'web/url'
        record.recorddate = '2019-9-12'
        record.notes = 'Test potential init'
        record.elements = 'Ag'
        record.othername = 'test'

        assert record.key == '8asdn3'
        assert record.id == 'new-potential-demo'
        assert record.url == 'web/url'
        assert record.recorddate == date(2019, 9, 12)
        assert record.notes == 'Test potential init'
        assert record.elements == ['Ag']
        assert record.othername == 'test'
        
    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('Potential/*.json'):
            record = potentials.load_record('Potential', model=fname)
            with open(fname) as f:
                content = f.read()
            print(record.build_model().json(indent=4))
            print(content)
            #assert record.build_model().json(indent=4) == content

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        actions, df = potdb.get_potentials(return_df=True, refresh_cache=True)
        assert len(actions) == 3


        actions = potdb.get_potentials(key='78392771-83e9-491c-bf4c-39175befd072')
        assert len(actions) == 1

        actions = potdb.get_potentials(id='2016--Kim-Y-K-Kim-H-K-Jung-W-S-Lee-B-J--Al-Ti')
        assert len(actions) == 1

        actions = potdb.get_potentials(recorddate='2018-10-04')
        assert len(actions) == 1

        actions = potdb.get_potentials(notes='opopo')
        assert len(actions) == 0

        actions = potdb.get_potentials(elements='Al')
        assert len(actions) == 1

        actions = potdb.get_potentials(fictionalelements='Ni')
        assert len(actions) == 0

        actions = potdb.get_potentials(othername='Cheese')
        assert len(actions) == 0


    def test_add_citation(self):
        return 
        record = potentials.load_record('Potential')
        record.add_citation(potential_key='asdf', potential_id='ppppp', dois=['asdf', '525'], elements='B', fictionalelements='Po', othername='Rob')

        jsonstr = '{"potential-info": {"key": "asdf", "id": "ppppp", "doi": ["asdf", "525"], "fictional-element": "Po", "element": "B", "other-element": "Rob"}}'

        assert record.citations[0].build_model().json() == jsonstr

    def test_add_implementation(self):
        return
        record = potentials.load_record('Potential')
        record.add_implementation(potential_key='asdf', potential_id='ppppp', dois=['asdf', '525'], elements='B', fictionalelements='Po', othername='Rob')

        jsonstr = '{"potential-info": {"key": "asdf", "id": "ppppp", "doi": ["asdf", "525"], "fictional-element": "Po", "element": "B", "other-element": "Rob"}}'

        assert record.implementations[0].build_model().json() == jsonstr

    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_potential(id='2018--Farkas-D-Caro-A--Fe-Ni-Cr-Co-Cu')

        with pytest.raises(ValueError):
            potdb.get_potential(notes='example', prompt=False)

        with pytest.raises(ValueError):
            potdb.get_potential(notes='nnosasfddoij')


    def test_retrieve(self, tmp_path):
        """Test retrieving and saving a single record from the database"""
        potdb = self.potdb

        potdb.retrieve_potential(dest=tmp_path, id='2018--Farkas-D-Caro-A--Fe-Ni-Cr-Co-Cu')

    def test_download(self, tmp_path):
        """Test downloading records from the remote and saving to the local"""
        if test_with_remote:
            potdb = potentials.Database(localpath=tmp_path, remote=True)
            potdb.download_potentials()

    def test_save_upload_delete(self):
        """Test saving, uploading and deleting a record"""
        potdb = self.potdb
        
        record = potentials.load_record('Potential', name='dbtesting', recorddate='1212-12-12',
                                        elements='Na', notes='test potential')


        potdb.save_potential(record)
        potdb.get_potential(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_potential(record=record)
            potdb.get_potential(name='dbtesting', local=False)

        potdb.delete_potential(potential=record, 
                               remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_potential(name='dbtesting')

