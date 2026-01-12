# SPAAS Frontend

Modern Next.js frontend for SPAAS hypercube suppression method.

## Features

- 🎨 Beautiful, modern UI with Tailwind CSS
- 📤 Drag-and-drop file upload
- 🔧 Interactive protection rules configuration
- 📊 Real-time results display with statistics
- 📥 One-click download of suppressed data
- 📱 Responsive design (works on mobile, tablet, desktop)

## Quick Start

### 1. Start the Backend

First, make sure the Python backend is running:

```powershell
# From C:\SPAAS directory
cd backend
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### 2. Start the Frontend

In a new terminal:

```powershell
# From C:\SPAAS\frontend directory
cd C:\SPAAS\frontend
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Open in Browser

Navigate to http://localhost:3000 in your web browser.

## Usage

1. **Upload File**: Click or drag-and-drop a CSV or Excel file
2. **Configure Rules**: Adjust protection rules using sliders and inputs
3. **Run Suppression**: Click "Run Hypercube Suppression"
4. **View Results**: See statistics and preview suppressed data
5. **Download**: Click "Download Suppressed Data" to get CSV file

## Protection Rules

### Minimum Frequency
- Cells with values below this threshold will be suppressed
- Higher value = more suppressions
- Default: 3

### Dominance N
- Number of top contributors to check
- Options: 1 (single), 2 (top 2), 3 (top 3)
- Default: 1

### Dominance K%
- Percentage threshold for top N contributors
- Lower value = stricter (more suppressions)
- Range: 50% - 95%
- Default: 80%

### P-Percent %
- Estimation threshold for back-calculation protection
- Lower value = stricter (more suppressions)
- Range: 5% - 20%
- Default: 10%

## File Requirements

- **Formats**: CSV (.csv) or Excel (.xlsx)
- **Structure**: Tabular data with numeric values
- **Size**: No strict limit (tested up to 10MB)

## Components

### FileUpload.tsx
- Drag-and-drop file upload
- File validation (CSV/Excel only)
- Visual feedback

### ProtectionRulesConfig.tsx
- Interactive sliders for thresholds
- Number inputs for precise values
- Reset to defaults button

### ResultsDisplay.tsx
- Statistics cards (Total, Primary, Secondary, Total Suppressions)
- Suppression rate progress bar
- Data preview table with highlighted suppressions
- Legend explaining suppression markers

## Development

### Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page
│   └── globals.css         # Global styles
├── components/
│   ├── FileUpload.tsx      # File upload component
│   ├── ProtectionRulesConfig.tsx  # Rules configuration
│   └── ResultsDisplay.tsx  # Results display
├── public/                 # Static assets
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript config
```

### Technologies

- **Next.js 15**: React framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS
- **React Hooks**: State management

### Build for Production

```powershell
npm run build
npm start
```

## Troubleshooting

### Backend Connection Error

If you see "Failed to process file":
1. Ensure backend is running on port 8000
2. Check CORS settings in `backend/app/main.py`
3. Verify file format is CSV or Excel

### Frontend Won't Start

```powershell
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### Styling Issues

```powershell
# Rebuild Tailwind CSS
npm run build
```

## Future Enhancements

- [ ] Real-time progress updates via WebSocket
- [ ] Multiple method selection (Modular, Optimal)
- [ ] Data visualization charts
- [ ] Batch processing
- [ ] User authentication
- [ ] Save/load configuration presets

## Support

For issues or questions, refer to the main SPAAS documentation in `C:\SPAAS\README.md`
