import pytest
from unittest.mock import patch
from patient_generator import nhanes_stats
from patient_generator import db_utils

DATA_COUNTS_BY_VARIABLE =  [{'Variable': 'RIDAGEYR', 'TableName': 'DEMO_H', 'CodeOrValue': '0 to 79', 
                            'Count': 9823, 'ValueDescription': 'Range of Values', 'SasLabel': 'Age in years at screening'}, 
                            {'Variable': 'RIDAGEYR', 'TableName': 'DEMO_H', 'CodeOrValue': '80', 'Count': 352, 
                             'ValueDescription': '80 years of age and over', 'SasLabel': 'Age in years at screening'}, 
                            {'Variable': 'RIDAGEYR', 'TableName': 'DEMO_H', 'CodeOrValue': '.', 'Count': 0, 
                             'ValueDescription': 'Missing', 'SasLabel': 'Age in years at screening'}]

class MockCursor:
    def __init__(self, query_name=None):
        self.query_name = query_name

    def execute(self, query, params=None):
        self.query_name = "data_counts_by_variable" if "Metadata" in repr(query) else "data_for_range"
    
    def fetchall(self):
        return DATA_COUNTS_BY_VARIABLE if self.query_name == 'data_counts_by_variable' else [(x, ) for x in range(0, 79)]

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class MockInterface(db_utils.DBInterface):
    def get_connection(self):
        return MockConnection()
    
class MockConnection:
    def cursor(self, cursor_factory=None):
        return MockCursor()

def test_data_for_variable():
    with patch.object(nhanes_stats, 'db_interface', MockInterface()):
        table_name, variable = 'DEMO_H', 'RIDAGEYR'
        result = nhanes_stats.data_for_variable(table_name, variable)
        assert result[0]['Variable'] == 'RIDAGEYR'
        assert result[0]['TableName'] == 'DEMO_H'
        assert result[0]['CodeOrValue'] == '0 to 79'
        assert result[0]['Count'] == 9823
        assert result[0]['ValueDescription'] == 'Range of Values'
        assert 'stats' in result[0]
        assert result[0]['stats']['mean'] == 39.0
        assert result[0]['stats']['stdev'] == pytest.approx(22.95, 0.01)
        assert result[0]['stats']['median'] == 39
        assert result[0]['stats']['mode'] == 0
        assert result[0]['stats']['quartiles'] == [19.5, 39, 58.5]

        assert result[1]['Variable'] == 'RIDAGEYR'
        assert result[1]['TableName'] == 'DEMO_H'
        assert result[1]['CodeOrValue'] == '80'
        assert result[1]['Count'] == 352
        assert result[1]['ValueDescription'] == '80 years of age and over'
        assert 'stats' not in result[1]

        assert len(result) < 3