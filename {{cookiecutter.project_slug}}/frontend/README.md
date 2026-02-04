# ProjectMaker} Frontend

A React frontend for ProjectMaker} - a web-based application for building, visualizing, and managing complex narratives.

## Features

- **Authentication**: Phone number-based authentication with SMS/WhatsApp verification
- **User Registration**: Complete signup flow with account verification
- **Modern UI**: Built with React, TypeScript, Tailwind CSS, and Redux
- **Responsive Design**: Mobile-first approach with beautiful, modern interface

## Technology Stack

- React 19 with TypeScript
- Redux Toolkit for state management
- React Router for navigation
- Tailwind CSS for styling
- Axios for API communication

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Update the API URL in `.env`:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Development

Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── LoginForm.tsx   # Login form component
│   ├── SignUpForm.tsx  # Signup form component
│   └── Dashboard.tsx   # Main dashboard component
├── pages/              # Page components
│   └── AuthPage.tsx    # Authentication page wrapper
├── store/              # Redux store configuration
│   ├── authSlice.ts    # Authentication state management
│   ├── index.ts        # Store configuration
│   └── hooks.ts        # Typed Redux hooks
├── services/           # API services
│   └── api.ts          # API client configuration
├── types/              # TypeScript type definitions
│   └── auth.ts         # Authentication types
└── App.tsx             # Main app component
```

## Authentication Flow

1. **Login**: Users enter their phone number, receive a verification code, and enter it to sign in
2. **Signup**: New users provide their details, create an account, and verify it with a code
3. **Dashboard**: Authenticated users access the main application interface

## API Integration

The frontend communicates with the Django REST API backend using:
- Cookie-based authentication with JWT tokens
- Automatic token refresh handling
- Error handling and user feedback

### Authentication Provider Values

The frontend uses the correct short values for external authentication providers that match the Django backend:

- `SMS` - SMS verification
- `WH` - WhatsApp verification  
- `D` - Console verification (Development only)

These values are defined in `src/utils/constants.ts` and used throughout the application.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the ProjectMaker} application.
