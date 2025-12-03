# AutoML Platform - Frontend

Modern React frontend for the AutoML No-Code Platform.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

## Development

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

Access at: http://localhost:3000

### Build for Production
```bash
npm run build
```

Output: `dist/` directory

### Run Tests
```bash
npm test
```

### Lint Code
```bash
npm run lint
npm run lint:fix
```

### Format Code
```bash
npm run format
```

## Project Structure

```
src/
├── components/          # Reusable components
│   └── Layout.jsx      # Main layout with header/footer
├── pages/              # Page components
│   ├── HomePage.jsx    # Landing page
│   ├── NewRunPage.jsx  # Start new ML run
│   ├── RunDetailsPage.jsx  # Run status & results
│   └── RunsListPage.jsx    # List all runs
├── services/           # API services
│   └── api.js          # Backend API client
├── App.jsx             # Main app component
├── main.jsx            # Entry point
└── index.css           # Global styles
```

## API Integration

The frontend communicates with the FastAPI backend through a proxy:

**Development**: `/api/*` → `http://localhost:8000/*`
**Production**: Served from same origin

See `vite.config.js` for proxy configuration.

## Environment Variables

Create `.env` file:

```bash
VITE_API_URL=/api
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run format` - Format code

## Features

- ✅ Responsive design
- ✅ Real-time status updates
- ✅ File upload support
- ✅ Form validation
- ✅ Error handling
- ✅ Loading states
- ✅ Dark mode ready

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

## License

MIT
