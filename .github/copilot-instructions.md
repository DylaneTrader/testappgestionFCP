# Copilot Instructions - Gestion FCP

## Project Overview
Django application for managing **Fonds Communs de Placement (FCP)** - mutual funds for CGF Bourse. Displays Net Asset Values (VL - Valeurs Liquidatives), performance metrics, and generates professional factsheets/reports.

## Architecture

### Data Model Pattern (Critical)
- **One VL table per FCP**: Each of the 25 funds has its own model class inheriting from `BaseValeurLiquidative`
- Use `FCP_VL_MODELS` dict in [fcp_app/models.py](fcp_app/models.py) to map FCP names to model classes
- Use `get_vl_model(fcp_name)` helper to retrieve the correct model dynamically
- `FicheSignaletique` holds fund metadata (risk scale, type, benchmark allocations)

```python
# Correct pattern for accessing VL data
from fcp_app.models import get_vl_model, FCP_VL_MODELS
vl_model = get_vl_model("FCP PLACEMENT AVANTAGE")
vl_data = vl_model.objects.all().order_by('date')
```

### Static Data Source
- [fcp_app/data.py](fcp_app/data.py) contains `FCP_FICHE_SIGNALETIQUE` dict with fund metadata
- Sync to database via: `python manage.py populate_fcp`

## Key Commands

```bash
# Setup
python manage.py migrate
python manage.py populate_fcp          # Load fund metadata from data.py
python manage.py import_vl --file=data.xlsx  # Import VL from Excel
python manage.py import_vl --clear     # Clear existing VL before import

# Run
python manage.py runserver
```

## API Conventions
All API endpoints in [fcp_app/views.py](fcp_app/views.py):
- Prefix: `/api/` (e.g., `/api/vl-data/`, `/api/export-pdf/`)
- Return `JsonResponse` for data, `HttpResponse` with appropriate MIME type for exports
- FCP selection via `?fcp=FCP%20NAME` query parameter

## Performance Calculation Patterns
Two types of performance metrics calculated in views:
- **Glissantes (Rolling)**: 1m, 3m, 6m, 1y, 3y, 5y from last VL date
- **Calendaires (To-Date)**: WTD, MTD, QTD, STD, YTD based on calendar periods

## Frontend Stack
- Bootstrap 5 + Bootstrap Icons
- Chart.js for visualizations (loaded via CDN)
- Templates in [fcp_app/templates/fcp_app/](fcp_app/templates/fcp_app/)
- Custom styles: [fcp_app/static/fcp_app/css/style.css](fcp_app/static/fcp_app/css/style.css)

## Naming Conventions
- FCP names use uppercase with spaces: `"FCP PLACEMENT AVANTAGE"`
- VL model classes: `VL_FCP_<Name>` (underscores, PascalCase)
- Database tables: `fcp_app_vl_<lowercase_name>`
- Currency: XOF (West African CFA franc)

## Export Formats
Views support multiple export formats:
- CSV/Excel via `api_export_data`
- PowerPoint via `api_export_ppt` (python-pptx)
- PDF factsheets via `api_export_pdf`/`api_export_factsheet`

## Adding a New FCP
1. Add entry to `FCP_FICHE_SIGNALETIQUE` in [fcp_app/data.py](fcp_app/data.py)
2. Create new `VL_FCP_<Name>` model class in [fcp_app/models.py](fcp_app/models.py)
3. Add mapping to `FCP_VL_MODELS` dict
4. Run `python manage.py makemigrations && python manage.py migrate`
5. Run `python manage.py populate_fcp`
