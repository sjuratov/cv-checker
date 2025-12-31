# CV Checker Frontend

Modern, responsive web interface for the CV Checker application built with React, TypeScript, and Vite.

## Features

### Phase 2 Implementation

✅ **CV Upload Interface**
- Drag-and-drop Markdown file upload
- File validation (format, size)
- Visual feedback and error handling

✅ **Job Description Input**
- Multi-line text area with character counter
- Real-time validation
- Clear and reset functionality

✅ **Analysis Trigger**
- Smart button enabling based on prerequisites
- Loading states with status messages
- Error handling with retry mechanism

✅ **Results Display**
- Overall match score with visual gauge
- Subscores breakdown (Skills, Experience, Education)
- Top 3 strengths and improvement areas
- Detailed recommendations with priority indicators
- Expandable recommendation cards

✅ **Analysis History**
- Local storage of last 10 analyses
- Sortable analysis list
- View past analysis details
- Score comparison at a glance

✅ **Responsive Design**
- Mobile-first approach
- Tablet and desktop optimizations
- Touch-friendly interface

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Zustand** - State management
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **LocalStorage** - Client-side persistence

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Backend running at `http://localhost:8000` (see [backend/README.md](../backend/README.md))

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Start development server
npm run dev
```

The application will be available at [http://localhost:5173](http://localhost:5173)

### Environment Variables

Create a `.env.local` file with:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
```

## Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

### Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── upload/          # Upload-related components
│   │   ├── results/         # Results display components
│   │   ├── history/         # History view components
│   │   └── views/           # Main view components
│   ├── lib/                 # API client
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main app component
│   ├── App.css              # Application styles
│   └── main.tsx             # Application entry point
├── public/                  # Static assets
├── .env.example             # Environment template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
└── vite.config.ts           # Vite config
```

## Usage

### 1. Upload CV

- Click "Choose File" or drag-and-drop a Markdown (.md) file
- File must be < 2MB and contain at least 100 characters
- CV content is stored locally for the session

### 2. Enter Job Description

- Paste job description into the text area
- Minimum 50 characters, maximum 10,000 characters
- Character counter shows real-time progress

### 3. Analyze

- Click "Analyze Match" when both CV and job description are provided
- Wait 20-30 seconds for AI analysis to complete
- Results display automatically

### 4. View Results

- **Overall Score**: 0-100 match score with visual gauge
- **Subscores**: Skills, Experience, Education breakdowns
- **Strengths**: Top 3 strong points
- **Gaps**: Top 3 areas to improve
- **Recommendations**: Actionable suggestions with priority levels

### 5. Review History

- Click "History" to view past analyses
- Last 10 analyses stored in browser localStorage
- Click any analysis to view full details

## API Integration

The frontend integrates with the FastAPI backend using a type-safe API client.

### Endpoint: POST /api/v1/analyze

**Request:**
```typescript
{
  cv_markdown: string;      // 100-50,000 chars
  job_description: string;  // 50-10,000 chars
}
```

**Response:**
```typescript
{
  analysis_id: string;
  overall_score: number;         // 0-100
  skill_matches: SkillMatch[];
  experience_match: object;
  education_match: object;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
}
```

## State Management

The app uses Zustand for state management with localStorage persistence:

- **CV State**: Current uploaded CV (filename, content, timestamp)
- **Job State**: Current job description
- **Analysis State**: Loading status, error, result
- **History State**: Last 10 analysis results

## Styling

Custom CSS with responsive breakpoints:

- **Mobile**: 320px - 767px (single column)
- **Tablet**: 768px - 1023px (two columns)
- **Desktop**: 1024px+ (optimized layout)

Color-coded scoring:
- 🔴 Red (0-49): Poor match
- 🟡 Yellow (50-74): Fair match
- 🟢 Green (75-89): Good match
- 🔵 Blue (90-100): Excellent match

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment

The frontend is designed to be deployed to **Azure Static Web Apps**.

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

## Troubleshooting

### Backend Connection Issues

If you see "Unable to connect to server":
1. Verify backend is running at `http://localhost:8000`
2. Check CORS configuration in backend
3. Verify `VITE_API_BASE_URL` in `.env.local`

### File Upload Errors

- Ensure file is Markdown (.md) format
- Check file size < 2MB
- Verify CV content has at least 100 characters

### Analysis Timeout

- Normal analysis takes 20-30 seconds
- Timeout set to 60 seconds
- Retry if timeout occurs

## License

MIT License - see [LICENSE.md](../LICENSE.md)
