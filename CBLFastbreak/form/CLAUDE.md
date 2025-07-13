# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **CBL 2025 Corporate Tournament Registration Form** - a Next.js 14 application with App Router that handles multi-step team registration, Google Sheets integration, and file uploads. It's designed for basketball corporate tournament registration with authentication and data persistence.

## Commands

### Development
- `npm run dev` - Start development server on localhost:3000
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint for code linting

### Package Manager
- Uses **pnpm** (pnpm-lock.yaml present)
- Install dependencies: `pnpm install`

## Architecture

### Core Structure
- **Next.js 14 App Router** with TypeScript
- **Multi-step form flow**: Landing → Step 1 (Team Info) → Step 2 (Players) → Step 3 (Payment) → Confirmation
- **Server Actions** for form submission (`app/actions.ts`)
- **Google OAuth 2.0** authentication with NextAuth.js
- **Data persistence** via Google Sheets API integration

### Key Directories
- `app/` - Next.js App Router pages and API routes
  - `register/step[1-3]/` - Multi-step registration flow
  - `register/confirmation/` - Final confirmation page
  - `api/auth/` - NextAuth.js authentication endpoints
  - `lib/userData.ts` - Google Sheets user data management
- `components/ui/` - shadcn/ui component library (complete set)
- `hooks/` - Custom React hooks
- `public/` - Static assets including CBL logo

### Authentication Flow
- Google OAuth 2.0 via NextAuth.js
- Session management with server-side session checking
- User form data persistence per Google account
- Auto-population of previously saved form data

### Data Integration
- **Google Sheets API** for both:
  - Final registration submissions (main sheet)
  - User form data persistence (UserData sheet)
- **Vercel Blob** for payment file uploads (PDF, JPG, PNG up to 10MB)
- Server Actions handle all backend operations

### UI Framework
- **Tailwind CSS** for styling
- **shadcn/ui** complete component library
- **React Hook Form** with Zod validation
- **Next Themes** for theme support
- **Lucide React** for icons

## Environment Variables Required

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-key

# Google OAuth (for authentication)
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-client-secret

# Google Sheets API (for data storage)
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----
GOOGLE_SHEET_ID=your-google-sheet-id

# Vercel Blob (for file uploads)
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

## Form Data Structure

### Registration Flow
1. **Step 1**: Team name, company details (primary + optional secondary)
2. **Step 2**: Player details (up to 15 players with full contact info and affiliation)
3. **Step 3**: Payment proof file upload
4. **Confirmation**: Final validation and submission

### Data Models
- Players: fullName, icPassport, email, phone, affiliationType
- Team: teamName, company1, company2 (optional)
- File uploads: Secured via Vercel Blob with public URLs

## Configuration Notes

- **TypeScript**: Strict mode enabled with path aliases (`@/*`)
- **Next.js**: Static export ready, ESLint/TypeScript errors ignored during builds for deployment flexibility
- **Images**: Optimized for Vercel Blob domains, unoptimized for static export compatibility
- **Server Actions**: Configured for localhost and Vercel domains

## Development Setup

1. Install dependencies: `pnpm install`
2. Copy environment variables to `.env.local`
3. Set up Google OAuth 2.0 (see GOOGLE_OAUTH_SETUP.md)
4. Configure Google Sheets API service account
5. Set up Vercel Blob storage
6. Run development: `npm run dev`

## Deployment

### Cloudflare Pages (Primary)
- **Build command**: `npm run build`
- **Output directory**: `out`
- **Node.js version**: 18.x
- **Auto-deployment**: Connected to GitHub repository
- Requires all environment variables to be set in Cloudflare Pages dashboard

### Alternative Deployments
- **Vercel**: `npm run build && vercel --prod`
- **Static export**: `npm run build` (configured for static hosting)
- Requires all environment variables to be set in deployment platform