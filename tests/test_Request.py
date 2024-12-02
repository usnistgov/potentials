from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestRequest():

    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        record = potentials.load_record('Request')

        assert record.style == 'Request'
        assert record.modelroot == 'request'
        assert record.date == date.today()
        assert record.comment is None
        assert len(record.systems) == 0

    def test_assign_init(self):
        """Test value assignment during init"""
        
        record = potentials.load_record('Request', date='1212-12-12',
                                        comment='for simulating')
    
        assert record.date == date(1212, 12, 12)
        assert record.comment == 'for simulating'

        jsonmodel = '{"request": {"date": "1212-12-12", "comment": "for simulating"}}'

        assert record.build_model().json() == jsonmodel
        assert record.model.json() == jsonmodel

        meta = record.metadata()
        assert meta['date'] == date(1212, 12, 12)
        assert meta['comment'] == 'for simulating'
        assert len(meta['systems']) == 0


    def test_assign(self):
        """Test value assignment after init"""
        record = potentials.load_record('Request')

        record.name = 'req'
        record.date = "1212-12-12"
        record.comment = 'for simulating'
        assert record.name == 'req'
        assert record.date == date(1212, 12, 12)
        assert record.comment == 'for simulating'


    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('Request/*.json'):
            record = potentials.load_record('Request', model=fname)
            with open(fname) as f:
                content = f.read()
            assert record.build_model().json(indent=4) == content, record.build_model().json(indent=4)

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        records, df = potdb.get_requests(return_df=True, refresh_cache=True)
        assert len(records) == 3

        records = potdb.get_requests(name='2020-12-30 Bi')
        assert len(records) == 1

        records = potdb.get_requests(date='2021-03-04')
        assert len(records) == 1

        records = potdb.get_requests(comment='Buckingham')
        assert len(records) == 1

        records = potdb.get_requests(formula='Y2Zr2O7')
        assert len(records) == 1

        records = potdb.get_requests(elements='Bi')
        assert len(records) == 1

    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_request(elements='Mg')

        with pytest.raises(ValueError):
            potdb.get_request(date=['2021-03-04', '2022-05-28'], prompt=False)

        with pytest.raises(ValueError):
            potdb.get_request(comment='nnosasfddoij')


    def test_retrieve(self, tmp_path):
        """Test retrieving and saving a single record from the database"""
        potdb = self.potdb

        potdb.retrieve_request(dest=tmp_path, comment='Buckingham')

    def test_download(self, tmp_path):
        """Test downloading records from the remote and saving to the local"""
        if test_with_remote:
            potdb = potentials.Database(localpath=tmp_path, remote=True)
            potdb.download_requests()

    def test_save_upload_delete(self):
        """Test saving, uploading and deleting a record"""
        potdb = self.potdb
        
        record = potentials.load_record('Request', name='dbtesting', date='1212-12-12',
                                        comment='a test record for database operations')


        potdb.save_request(record)
        potdb.get_request(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_request(request=record)
            potdb.get_request(name='dbtesting', local=False)

        potdb.delete_request(request=record, 
                             remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_request(name='dbtesting')

