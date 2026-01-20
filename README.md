# SPAAS Modernized

**Secondary Protection as a Service** - Modern Python Implementation

A complete rewrite of SPAAS (originally C++/Fortran) using Python, FastAPI, and Next.js for Windows Server deployment at Eurostat.

---

## 🎯 Project Overview

**Goal**: Modernize statistical disclosure control system with 10-500x performance improvement while maintaining full compatibility with τ-ARGUS workflows.

**Current Status**: 
- ✅ Phase 1 Complete: Hypercube method implemented (537 lines Python)
- ✅ Web interface operational (FastAPI + Next.js)
- ✅ 4 test scenarios passing
- ⏳ Batch mode in development (Week 1 of 6)

---

## 📂 Project Structure

```
C:\SPAAS\
│
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── hypercube.py           # ✅ Hypercube suppression engine
│   │   ├── main.py                # ✅ FastAPI application
│   │   ├── schemas.py             # ⏳ Data models
│   │   └── tauargus_formats.py    # 🆕 τ-ARGUS format handlers
│   ├── requirements.txt
│   └── .env
│
├── frontend/                # Next.js web interface
│   ├── src/
│   │   ├── app/                   # ✅ App router
│   │   └── components/            # ✅ React components
│   ├── package.json
│   └── next.config.js
│
├── tests/                   # Automated tests
│   ├── test_hypercube.py          # ✅ Hypercube tests
│   ├── test_formats.py            # ⏳ Format parser tests
│   └── test_batch.py              # ⏳ Batch mode tests
│
├── docs/                    # 📚 All documentation
│   ├── README.md                       # Documentation index
│   ├── COMPLETE_SPAAS_APPROACH.md      # Complete technical approach
│   ├── TAUARGUS_INTEGRATION_ANALYSIS.md # τ-ARGUS integration guide
│   ├── PROJECT_STATUS_SUMMARY.md       # Current status
│   └── BATCH_MODE_QUICKSTART.md        # Batch mode guide
│
├── test_data/               # 🧪 Test datasets
│   ├── simple/                    # Unit test data
│   ├── batch/                     # Batch test files (.arb)
│   ├── reference/                 # τ-ARGUS reference data
│   └── README.md                  # Test data guide
│
├── .gitignore
└── README.md                # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup
```powershell
cd C:\SPAAS\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```powershell
cd C:\SPAAS\frontend
npm install
npm run dev
```

### Access Application
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 📖 Documentation

All documentation is in the **`/docs/`** folder:

| Document | Purpose |
|----------|---------|
| **COMPLETE_SPAAS_APPROACH.md** | Full technical approach for all methods |
| **TAUARGUS_INTEGRATION_ANALYSIS.md** | τ-ARGUS compatibility & file formats |
| **PROJECT_STATUS_SUMMARY.md** | What's implemented vs planned |
| **BATCH_MODE_QUICKSTART.md** | Step-by-step batch mode guide |

**Start Here**: `docs/BATCH_MODE_QUICKSTART.md` for immediate next steps

---

## 🧪 Testing

### Run Tests
```powershell
cd C:\SPAAS\backend
python -m pytest tests/ -v
```

### Test Data
All test data is organized in **`/test_data/`**:
- `/simple/` - Unit test cases
- `/batch/` - Batch mode tests (.arb files)
- `/reference/` - τ-ARGUS reference datasets

See `test_data/README.md` for details.

---

## 🎯 Current Implementation Status

### ✅ Completed (Phase 1)
- [x] Hypercube secondary suppression
- [x] Primary suppression (frequency, dominance, p-percent rules)
- [x] Web UI (upload, configure, download)
- [x] FastAPI REST endpoints
- [x] Basic CSV/Excel support

### ⏳ In Progress (Phase 2 - Weeks 1-2)
- [ ] τ-ARGUS format handlers (.asc, .rda, .tab, .hrc, .sbs)
- [ ] Batch file parser (.arb)
- [ ] Batch API endpoint
- [ ] Shadow/holding/weight variable support

### 📅 Planned
- **Phase 3** (Weeks 3-4): Hierarchies & advanced features
- **Phase 4** (Weeks 5-6): Testing & validation
- **Phase 5**: Modular and Optimal methods

---

## 🏗️ Architecture

### Backend (Python)
- **FastAPI** - Modern async web framework
- **NumPy/Pandas** - Data processing
- **NetworkX** - Graph algorithms (hypercube)
- **OR-Tools** - Optimization engine (SCIP/CBC)

### Frontend (TypeScript)
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **Plotly.js** - Visualizations

### Deployment
- **Windows Server** (primary target)
- **Azure Cloud** (optional)

---

## 📊 Performance Targets

| Method | Original (C++/Fortran) | Target (Python) | Speedup |
|--------|----------------------|-----------------|---------|
| Hypercube | ~8 sec (1K cells) | <0.5 sec | **16x** |
| Hypercube | ~45 sec (10K cells) | <3 sec | **15x** |
| Hypercube | ~6 min (100K cells) | <20 sec | **18x** |

---

## 🤝 Development Workflow

### 1. Read Documentation
Start with `docs/BATCH_MODE_QUICKSTART.md`

### 2. Create Feature Branch
```powershell
git checkout -b feature/batch-parser
```

### 3. Implement & Test
```powershell
# Make changes
python -m pytest tests/ -v
```

### 4. Update Documentation
Mark completed tasks in `docs/PROJECT_STATUS_SUMMARY.md`

---

## 📝 File Format Support

### Input Formats
- ✅ CSV (current)
- ✅ Excel (.xlsx) (current)
- 🆕 τ-ARGUS microdata (.asc + .rda)
- 🆕 τ-ARGUS tabulated (.tab)
- 🆕 Hierarchies (.hrc)
- 🆕 A priori protection (.hst)

### Output Formats
- ✅ CSV (current)
- ✅ Excel with highlighting (current)
- 🆕 SBS format (Eurostat standard)
- 🆕 Code-value format

### Batch Processing
- 🆕 Batch files (.arb)
- 🆕 Full τ-ARGUS compatibility

---

## 🔧 Configuration

### Environment Variables
Create `.env` file in `backend/`:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Performance
MAX_WORKERS=4
TIMEOUT_SECONDS=300
```

---

## 📚 Additional Resources

### External Documentation
- **τ-ARGUS Manual**: `C:\Program Files\TauArgus\help\TauManualV4.1.pdf`
- **Original SPAAS**: `C:\Users\Nick\Documents\SPAAS-main`
- **τ-ARGUS Source**: `C:\Users\Nick\Documents\tauargus-master`

### Key Algorithms
- **Hypercube (GHMiter)**: De Wolf, P.P. (2002)
- **Optimal Method**: Fischetti & Salazar (2000)

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check Python version
python --version  # Must be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```powershell
# Clear cache and reinstall
rm -r node_modules
rm package-lock.json
npm install
```

### Tests failing
```powershell
# Run with verbose output
python -m pytest tests/ -v --tb=short
```

---

## 👥 Team

- **Foteini** - Python modernization (current developer)
- **Marco** - Original SPAAS implementation (Linux/C++/Fortran)
- **Stakeholder** - Eurostat

---

## 📄 License

[Specify license here]

---

## 🎯 Next Steps

1. ✅ **Done**: Format handlers created (`tauargus_formats.py`)
2. ⏳ **Now**: Test format handlers with simple data
3. ⏳ **Next**: Implement batch file parser (.arb)
4. ⏳ **Then**: Add batch API endpoint

**See**: `docs/BATCH_MODE_QUICKSTART.md` for detailed instructions

---

## 📞 Support

For questions or issues:
1. Check documentation in `/docs/`
2. Review test examples in `/test_data/`
3. Consult τ-ARGUS manual for file format questions

---

**Last Updated**: January 2026  
**Version**: 1.0.0 (Phase 1 Complete, Phase 2 In Progress)
