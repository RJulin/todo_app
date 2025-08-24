# Todo App Frontend

A Next.js-based frontend for the todo application.

## Features

- Modern React with TypeScript
- Tailwind CSS for styling
- Responsive design
- Real-time todo management
- Integration with FastAPI backend

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

- `app/` - Next.js app directory
- `components/` - React components
- `types/` - TypeScript type definitions
- `app/page.tsx` - Main page component
- `app/globals.css` - Global styles

## Backend Integration

The frontend is configured to communicate with the FastAPI backend running on `http://localhost:8000`. Make sure the backend is running before using the frontend. 