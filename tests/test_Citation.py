from pathlib import Path
import potentials
from datetime import date

import pytest

from common_values import testdb_host, test_with_remote


class TestCitation():

    potdb = potentials.Database(localpath=testdb_host, remote=test_with_remote)


    def test_default_init(self):
        """Create default record"""
        record = potentials.load_record('Citation')

        assert record.style == 'Citation'
        assert record.modelroot == 'citation'
        assert record.doctype is None
        assert record.title is None
        assert len(record.authors) == 0
        assert record.publication is None
        assert record.year is None
        assert record.month is None
        assert record.volume is None
        assert record.issue is None
        assert record.abstract is None
        assert record.pages is None
        assert record.doi is None
        assert record.bibtex is None
        


    def test_assign_init(self):
        """Test value assignment during init"""
        
        record = potentials.load_record('Citation',
                                        doctype = 'journal',
                                        title = 'Something something something turn into a pumpkin',
                                        publication = 'Who Wants to Know',
                                        year = '1650',
                                        month = '11',
                                        volume = '4',
                                        issue = '1',
                                        abstract = 'Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?',
                                        pages = '1-999',
                                        doi = '12.3456/wwtk.0asf8.08asfgj9')
    
        assert record.doctype == 'journal'
        assert record.title == 'Something something something turn into a pumpkin'
        assert len(record.authors) == 0
        assert record.publication == 'Who Wants to Know'
        assert record.year == 1650
        assert record.month == 11
        assert record.volume == '4'
        assert record.issue == '1'
        assert record.abstract == 'Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?'
        assert record.pages == '1-999'
        assert record.doi == '12.3456/wwtk.0asf8.08asfgj9'
    
        bibtex = '@article{1650-,\n doi = {12.3456/wwtk.0asf8.08asfgj9},\n journal = {Who Wants to Know},\n month = {November},\n number = {1},\n pages = {1-999},\n title = {Something something something turn into a pumpkin},\n volume = {4},\n year = {1650}\n}\n'
        record.build_bibtex()
        assert record.bibtex == bibtex, 'different bibtex'

        jsonmodel = '{"citation": {"document-type": "journal", "title": "Something something something turn into a pumpkin", "publication-name": "Who Wants to Know", "publication-date": {"year": 1650, "month": "--11"}, "volume": "4", "issue": "1", "abstract": "Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?", "pages": "1-999", "DOI": "12.3456/wwtk.0asf8.08asfgj9", "bibtex": "@article{1650-,\\n doi = {12.3456/wwtk.0asf8.08asfgj9},\\n journal = {Who Wants to Know},\\n month = {November},\\n number = {1},\\n pages = {1-999},\\n title = {Something something something turn into a pumpkin},\\n volume = {4},\\n year = {1650}\\n}\\n"}}'

        assert record.build_model().json() == jsonmodel, 'different model'
        assert record.model.json() == jsonmodel, 'different model'

        meta = record.metadata()
        assert meta['name'] == '12.3456_wwtk.0asf8.08asfgj9'
        assert meta['doctype'] == 'journal'
        assert meta['title'] == 'Something something something turn into a pumpkin'
        assert len(meta['authors']) == 0
        assert meta['publication'] == 'Who Wants to Know'
        assert meta['year'] == 1650
        assert meta['month'] == 11
        assert meta['volume'] == '4'
        assert meta['issue'] == '1'
        assert meta['abstract'] == 'Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?'
        assert meta['pages'] == '1-999'
        assert meta['doi'] == '12.3456/wwtk.0asf8.08asfgj9'

    def test_assign(self):
        """Test value assignment after init"""
        record = potentials.load_record('Citation')

        record.doctype = 'journal'
        record.title = 'Something something something turn into a pumpkin'
        record.publication = 'Who Wants to Know'
        record.year = 1650
        record.month = '11'
        record.volume = '4'
        record.issue = '1'
        record.abstract = 'Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?'
        record.pages = '1-999'
        record.doi = '12.3456/wwtk.0asf8.08asfgj9'
        
        assert record.doctype == 'journal'
        assert record.title == 'Something something something turn into a pumpkin'
        assert record.publication == 'Who Wants to Know'
        assert record.year == 1650
        assert record.month == 11
        assert record.volume == '4'
        assert record.issue == '1'
        assert record.abstract == 'Pumpkin spice lattes, cookies, muffins, pancakes, ice cream, breads and martinis. Pumpkin spice everywhere. Is is all a lie?'
        assert record.pages == '1-999'
        assert record.doi == '12.3456/wwtk.0asf8.08asfgj9'
        
        with pytest.raises(ValueError):
            record.doctype = 'unsupported'

    def test_load_model(self):
        """Manually load each record in the database and check that build_model exactly rebuilds it"""
        for fname in testdb_host.glob('Citation/*.json'):
            record = potentials.load_record('Citation', model=fname)
            #with open(fname) as f:
            #    content = f.read()
            oldmodel = record.model
            newmodel = record.build_model()
            for key in oldmodel[record.modelroot]:
                if key != 'bibtex':
                    assert str(oldmodel[record.modelroot][key]) == str(newmodel[record.modelroot][key]), key
            #print(record.build_model().json(indent=4))
            #print(content)
            #assert record.build_model().json(indent=4) == content

    def test_query(self):
        """Test getting from the database and query operations"""

        potdb = self.potdb

        records, df = potdb.get_citations(return_df=True, refresh_cache=True)
        assert len(records) == 3

        records = potdb.get_citations(doctype='journal')
        assert len(records) == 2

        records = potdb.get_citations(title='simulation')
        assert len(records) == 1

        records = potdb.get_citations(surname='Mendelev')
        assert len(records) == 1

        records = potdb.get_citations(publication='Philosophical Magazine')
        assert len(records) == 1

        records = potdb.get_citations(year=2023)
        assert len(records) == 1

        records = potdb.get_citations(volume=89)
        assert len(records) == 1

        records = potdb.get_citations(abstract='interatomic')
        assert len(records) == 1

        records = potdb.get_citations(doi='10.1080/14786430903260727')
        assert len(records) == 1

        records = potdb.get_citations(author='Last Name')
        assert len(records) == 1


    def test_add_author(self):
        record = potentials.load_record('Citation')
        record.add_author(givenname='P.T.', surname='Barnham')

        jsonstr = '{"author": {"given-name": "P.T.", "surname": "Barnham"}}'

        assert record.authors[0].build_model().json() == jsonstr

    def test_get_singular(self):
        potdb = self.potdb

        potdb.get_citation(author='Asta')

        with pytest.raises(ValueError):
            potdb.get_citation(doctype='journal', prompt=False)

        with pytest.raises(ValueError):
            potdb.get_citation(year='9999')


    def test_retrieve(self, tmp_path):
        """Test retrieving and saving a single record from the database"""
        potdb = self.potdb

        potdb.retrieve_citation(dest=tmp_path, doctype='unspecified')

    def test_download(self, tmp_path):
        """Test downloading records from the remote and saving to the local"""
        if test_with_remote:
            potdb = potentials.Database(localpath=tmp_path, remote=True)
            potdb.download_citations()

    def test_save_upload_delete(self):
        """Test saving, uploading and deleting a record"""
        potdb = self.potdb
        
        record = potentials.load_record('Citation',
                                        name='dbtesting',
                                        doctype='unspecified',
                                        title='test record for database operations',
                                        year=1012)


        potdb.save_citation(record)
        potdb.get_citation(name='dbtesting', remote=False)

        if test_with_remote:
            potdb.upload_citation(citation=record)
            potdb.get_citation(name='dbtesting', local=False)

        potdb.delete_citation(citation=record, 
                            remote=test_with_remote)

        with pytest.raises(ValueError):
            potdb.get_citation(name='dbtesting')