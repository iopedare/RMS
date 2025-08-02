# Data Directory

This directory contains all data files for the Retail Management System backend.

## Directory Structure

```
data/
├── README.md                    # This file
└── test_results/                # Test result files
    ├── error_handling_test_results.json
    ├── enhanced_failover_test_results.json
    └── failover_test_results.json
```

## Test Results

The `test_results/` folder contains JSON files with test execution results from various test scenarios:

- **error_handling_test_results.json**: Results from error handling and edge case testing
- **enhanced_failover_test_results.json**: Results from enhanced failover and recovery testing  
- **failover_test_results.json**: Results from basic failover and recovery testing

### Test Result Format

Each test result file contains:
- `timestamp`: When the test was executed
- `results`: Array of individual test results with status and details
- `summary`: Overall test summary with pass/fail counts and duration

### Usage

Test results are automatically generated when running test scripts:
- `python tests/error_handling_test_runner.py`
- `python tests/enhanced_failover_test_runner.py` 
- `python tests/failover_test_runner.py`

## Future Data Files

This directory structure is designed to accommodate future data files such as:
- Configuration files
- Sample data files
- Export/import data
- Log files
- Database backups

## File Organization Rules

1. **Test Results**: All test result JSON files go in `test_results/`
2. **Configuration**: Configuration files should go in a `config/` subfolder
3. **Sample Data**: Sample data files should go in a `sample_data/` subfolder
4. **Logs**: Log files should go in a `logs/` subfolder
5. **Exports**: Export files should go in an `exports/` subfolder 