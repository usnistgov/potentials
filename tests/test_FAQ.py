from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestFAQ():

    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        record = potentials.load_record('FAQ')

        assert record.style == 'FAQ'
        assert record.modelroot == 'faq'
        assert record.question is None
        assert record.answer is None

    def test_assign_init(self):
        """Test value assignment during init"""
        
        record = potentials.load_record('FAQ', name='why', 
                                     question='why?', answer='because')
    
        assert record.question == 'why?'
        assert record.answer == 'because'

        jsonmodel = '{"faq": {"question": "why?", "answer": "because"}}'

        assert record.build_model().json() == jsonmodel
        assert record.model.json() == jsonmodel

        meta = record.metadata()
        assert meta['name'] == 'why'
        assert meta['question'] == 'why?'
        assert meta['answer'] == 'because'


    def test_assign(self):
        """Test value assignment after init"""
        record = potentials.load_record('FAQ')

        record.name = 'why'
        record.question = 'why?'
        record.answer = 'because'
        assert record.name == 'why'
        assert record.question == 'why?'
        assert record.answer == 'because'


    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('FAQ/*.json'):
            record = potentials.load_record('FAQ', model=fname)
            with open(fname) as f:
                content = f.read()
            assert record.build_model().json(indent=4) == content, content

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        records, df = potdb.get_faqs(return_df=True, refresh_cache=True)
        assert len(records) == 3

        records = potdb.get_faqs(name='faq')
        assert len(records) == 1

        records = potdb.get_faqs(question='fuzzy')
        assert len(records) == 1

        records = potdb.get_faqs(answer='woodchuck')
        assert len(records) == 1


    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_faq(question='fuzzy')

        with pytest.raises(ValueError):
            potdb.get_faq(question='?', prompt=False)

        with pytest.raises(ValueError):
            potdb.get_faq(answer='nnosasfddoij')


    def test_retrieve(self, tmp_path):
        """Test retrieving and saving a single record from the database"""
        potdb = self.potdb

        potdb.retrieve_faq(dest=tmp_path, question='fuzzy')

    def test_download(self, tmp_path):
        """Test downloading records from the remote and saving to the local"""
        if test_with_remote:
            potdb = potentials.Database(localpath=tmp_path, remote=True)
            potdb.download_faqs()

    def test_save_upload_delete(self):
        """Test saving, uploading and deleting a record"""
        potdb = self.potdb
        
        record = potentials.load_record('FAQ', name='dbtesting', question='what is this?',
                                        answer='a test record for database operations')


        potdb.save_faq(record)
        potdb.get_faq(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_faq(faq=record)
            potdb.get_faq(name='dbtesting', local=False)

        potdb.delete_faq(faq=record, 
                         remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_faq(name='dbtesting')

