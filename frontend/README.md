# Retail Management System – Frontend

This is the frontend application for the Retail Management System, built with Flutter for Windows Desktop. It provides the user interface for POS, inventory management, reporting, and real-time sync with the backend.

## Features
- Modern desktop UI for retail operations
- POS, inventory, and reporting modules
- Real-time sync with backend
- Offline-first support

## Project Structure
- `lib/` – Main Dart source code (entry point: main.dart)
- `test/` – Unit and widget tests
- `assets/` – Images, fonts, and other static resources
- `build/` – Build outputs (ignored by git)
- `.gitignore` – Flutter/Dart-specific ignores
- `pubspec.yaml` – Project metadata and dependencies
- `README.md` – Project documentation

## Setup
1. Install Flutter SDK (see https://flutter.dev/)
2. Run the following commands:
   ```bash
   cd frontend
   flutter pub get
   flutter run -d windows
   ```

## Documentation & References
- [Business Logic](../docs/business_logic.md)
- [Implementation Plan](../docs/implementation_plan.md)
- [Project Workflow](../docs/workflow.md)
- [Project Rules](../docs/PROJECT_RULES.md)
- [Project Checklist](../docs/PROJECT_CHECKLIST.md)

## API Reference
- See `API_REFERENCE.md` (to be created) for details on frontend-backend communication, data models, and integration points.

## Architecture
- See `ARCHITECTURE.md` (to be created) for frontend architecture, navigation, and state management.

---

For more details, see the main project documentation and PRD.
