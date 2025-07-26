# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Project initialized
- Directory structure and documentation files created
- Added initial project rules, checklist, and step summaries
- Populated README.md, PROJECT_RULES.md, PROJECT_CHECKLIST.md, PRD, CHANGELOG.md, step_and_summary.md
- Reviewed and aligned PRD and implementation plan
- Set up automated testing environment (pytest, coverage, sample tests)
- Scaffolded core backend modules: models/, routes/, services/, utils/ with __init__.py files 
- Implemented Product model in models/product.py using SQLAlchemy (fields: id, name, sku, price, quantity, batch_number, expiry_date, created_at, updated_at) 
- Integrated SQLAlchemy with Flask in app.py, configured SQLite, and enabled automatic table creation on startup. 