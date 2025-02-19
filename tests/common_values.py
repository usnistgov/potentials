from pathlib import Path

test_directory = Path(__file__).parent
testdb_host = Path(test_directory, 'testdb').absolute()

test_with_remote = False