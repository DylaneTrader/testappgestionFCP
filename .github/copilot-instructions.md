# Copilot Instructions - Gestion FCP

## Project Overview

Django 6.0 application for managing Fonds Communs de Placement (FCP/mutual funds) in West Africa (CGF Bourse). Displays net asset values (valeurs liquidatives), portfolio composition, performance analytics, and exports factsheets to PDF/PPT. Language: French UI, French code comments.

## Architecture & Data Model

### Unique Table-per-FCP Pattern
**Critical:** Each FCP has its own VL (valeur liquidative) table - there are 25 separate VL model classes inheriting from `BaseValeurLiquidative` in [models.py](fcp_app/models.py#L96-L340). This violates typical Django normalization but is deliberate for performance and data isolation.

- `FicheSignaletique`: Metadata for all FCPs (risk scale, fund type, benchmarks)
- `VL_FCP_*`: 25 separate VL tables (e.g., `VL_FCP_Placement_Avantage`, `VL_FCP_Actions_Pharmacie`)
- `FCP_VL_MODELS` dict in [models.py](fcp_app/models.py#L621-L646): Maps FCP name → model class
- Use `get_vl_model(fcp_name)` helper to retrieve the correct VL model

### Composition System
Four pocket types (Action, Obligation, Liquidité, FCP) stored in [CompositionPoche](fcp_app/models.py#L364-L394) with nested instruments (separate tables for each asset type):
- `InstrumentAction`: Equity holdings (ticker, sector, ISIN)
- `InstrumentObligation`: Bonds (issuer, maturity, nominal rate)
- `InstrumentLiquidite`: Cash equivalents (DAT, current accounts)
- `InstrumentFCP`: Fund-of-funds positions

### Benchmark System
Separate tables for [BenchmarkObligation](fcp_app/models.py#L592-L600) and [BenchmarkBRVM](fcp_app/models.py#L603-L611) (BRVM Composite index). FCP metadata stores target allocation percentages (`benchmark_oblig`, `benchmark_brvmc`).

## Critical Workflows

### Data Import (Non-SharePoint)
```bash
# 1. Initialize FCP metadata from hardcoded definitions
python manage.py populate_fcp

# 2. Bulk import VL from Excel (expects Date column + 25 FCP columns)
python manage.py import_vl --file data_fcp.xlsx --clear
```
[import_vl.py](fcp_app/management/commands/import_vl.py) uses pandas + bulk_create, maps Excel columns to FCP names via `FCP_VL_MODELS`.

### SharePoint Sync (Production Workflow)
```bash
python manage.py sync_vl_sharepoint \
  --site-url https://tenant.sharepoint.com/sites/Site \
  --file-path "Documents partages/VL/data.xlsx" \
  --sheet-name VL \
  --client-id $CLIENT_ID \
  --client-secret $SECRET \
  --tenant-id $TENANT_ID
```
[sync_vl_sharepoint.py](fcp_app/management/commands/sync_vl_sharepoint.py#L1-L100): Incremental inserts only (never updates/deletes), uses Office365-REST-Python-Client for auth, logs to `logs/sync_vl_sharepoint.log`.

### Database Operations
```bash
python manage.py migrate              # Apply schema changes
python manage.py runserver            # Dev server
python check_vl.py                    # Quick stats script (non-management command)
```

## Code Conventions

### Model Patterns
- **Abstract bases**: `BaseValeurLiquidative`, `BaseInstrument`, `BaseBenchmark` for shared fields
- **Related names**: Always use descriptive related_name (e.g., `related_name='vl_actions_pharmacie'`)
- **Verbose names**: French labels for Django admin (`verbose_name="Valeur Liquidative"`)
- **Meta ordering**: Always `ordering = ['-date']` for time series

### View Layer ([views.py](fcp_app/views.py))
- API endpoints return JSON (`JsonResponse`, no DRF)
- Performance calculations: WTD/MTD/QTD/STD/YTD (calendaires) + 1m/3m/6m/1y/3y/5y (glissantes)
- Tracking error = annualized volatility of daily returns (`(écart-type daily) * sqrt(365)`)
- Export functions: `api_export_ppt`, `api_export_pdf`, `api_export_factsheet` (uses python-pptx/reportlab)

### Frontend Integration
- Templates in [fcp_app/templates/fcp_app/](fcp_app/templates/fcp_app/)
- Static assets in [fcp_app/static/fcp_app/](fcp_app/static/fcp_app/) (CSS/JS)
- No JavaScript framework - vanilla JS with Chart.js for visualizations
- URLs follow pattern: `/` (VL page), `/composition/`, `/exportations/`, `/api/*`

## External Dependencies

- **pandas + openpyxl**: Excel file parsing
- **Office365-REST-Python-Client**: SharePoint OAuth2 + file download (requires Azure AD app registration)
- **Django 6.0**: Latest LTS (uses Python 3.11+)
- **SQLite**: Dev database only
- **PostgreSQL**: Production database (see migration section below)

## Data Flow: SharePoint → Database

All data originates from Excel files on SharePoint:
- **VL data**: Daily net asset values for all 25 FCPs
- **Benchmark data**: BRVM Composite and Obligation indices
- **Composition data**: Portfolio holdings by pocket type

Sync commands download Excel → parse with pandas → bulk insert to PostgreSQL.

## Development Gotchas

1. **Adding a new FCP**: 
   - Create VL model class inheriting `BaseValeurLiquidative`
   - Add to `FCP_VL_MODELS` dict
   - Create migration (`makemigrations`)
   - Add entry to `FCP_FICHE_SIGNALETIQUE` in [data.py](fcp_app/data.py)
   - Run `populate_fcp` command

2. **FCP name matching**: Must be EXACT (uppercase, spaces preserved) - names in Excel, `FCP_VL_MODELS`, and `FicheSignaletique.nom` must match perfectly

3. **Performance calculations**: Always use `.last()` not `.latest()` - models ordered by `-date` descending

4. **Decimal precision**: Financial values use `Decimal` type - never use float for VL/amounts

5. **Language**: Keep French terminology (e.g., "valeur liquidative" not "NAV", "échelle de risque" not "risk scale")

6. **SharePoint auth**: Requires pre-configured Azure AD app with Sites.Read.All permissions

## When Making Changes

- **New VL table**: Update migrations, `FCP_VL_MODELS`, `data.py`, and import scripts
- **New API endpoint**: Add to [urls.py](fcp_app/urls.py), follow JSON response pattern
- **New performance metric**: Add to both `perf_calendaires` and `perf_glissantes` in [views.py](fcp_app/views.py#L65-L125)
- **Schema changes**: Always use `makemigrations` + `migrate`, never manual SQL
- **Export formats**: Follow existing reportlab/python-pptx patterns in view functions

## Testing Approach

No formal test suite yet. Manual testing workflow:
1. Run `populate_fcp` + `import_vl` with sample Excel
2. Navigate to `/` and select different FCPs
3. Check `/composition/` and `/exportations/` pages
4. Verify JSON API responses in browser devtools

## Security Notes

- `SECRET_KEY` is exposed in [settings.py](gestionFCP/settings.py#L23) - must be env var in production
- `DEBUG = True` - disable for production
- SharePoint credentials passed via CLI args - use env vars or Azure Key Vault in production

## Secure Credential Setup (Production)

### Environment Variables
Create `.env` file (add to `.gitignore`):
```bash
# Django
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# PostgreSQL
DATABASE_URL=postgres://user:password@host:5432/gestion_fcp

# SharePoint Azure AD (App Registration)
SHAREPOINT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_SITE_URL=https://tenant.sharepoint.com/sites/YourSite
```

### Azure AD App Registration
1. Go to Azure Portal → Azure Active Directory → App registrations
2. New registration: "GestionFCP-SharePoint-Sync"
3. API permissions: Add `Sites.Read.All` (Application permission)
4. Grant admin consent
5. Certificates & secrets: Create new client secret (copy immediately)
6. Copy Application (client) ID and Directory (tenant) ID

### Load in settings.py
```python
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

## PostgreSQL Migration

### 1. Install dependencies
```bash
pip install psycopg2-binary dj-database-url python-dotenv
```

### 2. Update settings.py
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

### 3. Migrate data
```bash
# Export from SQLite
python manage.py dumpdata --natural-foreign --natural-primary -o backup.json

# Switch DATABASE_URL to PostgreSQL, then:
python manage.py migrate
python manage.py loaddata backup.json
```

## Testing

Run tests with:
```bash
python manage.py test fcp_app
python manage.py test fcp_app.tests.VLModelTests  # Specific test class
```

Tests cover:
- Model creation and constraints
- VL import workflow
- API endpoint responses
- Performance calculations accuracy
