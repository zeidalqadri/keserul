# CBL 2025 Corporate Tournament Registration Form

A complete registration form for the CBL 2025 Corporate Tournament with Google Sheets integration and file upload functionality.

## Features

- **Multi-section Form**: Team info, player details (up to 15), payment upload, confirmation
- **Google Sheets Integration**: Automatic data submission to connected spreadsheet
- **File Upload**: Secure payment proof upload with 10MB limit
- **Responsive Design**: Mobile-friendly with modern styling
- **Form Validation**: Real-time validation with error handling
- **Success Feedback**: Clear submission status messages

## Setup Instructions

### 1. Google Sheets Setup

1. Create a new Google Sheet with these column headers:
   - A1: Timestamp
   - B1: Team Name
   - C1: Company 1
   - D1: Company 2
   - E1: Players List
   - F1: Payment File URL

2. Create a Google Service Account:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select a project
   - Enable Google Sheets API
   - Create Service Account credentials
   - Download JSON key file

3. Share your Google Sheet with the service account email (from JSON file)
   - Give "Editor" permissions

### 2. Environment Variables

Create a `.env.local` file with:

\`\`\`env
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_SHEET_ID=your-sheet-id-from-url
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
\`\`\`

### 3. Deployment

#### Vercel (Recommended)
\`\`\`bash
npm run build
vercel --prod
\`\`\`

#### Cloudflare Pages
1. Build the static export:
\`\`\`bash
npm run build
npm run export
\`\`\`
2. Upload the `out` folder to Cloudflare Pages

## Form Sections

1. **Team Information**: Team name, company details, optional second company
2. **Player Details**: Up to 15 players with full details and affiliation
3. **Payment Upload**: Secure file upload for payment proof
4. **Confirmation**: Final validation and submission

## Technical Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components
- **Backend**: Next.js Server Actions
- **Storage**: Vercel Blob for file uploads
- **Integration**: Google Sheets API

## File Upload Specifications

- **Accepted formats**: PDF, JPG, PNG
- **Size limit**: 10MB maximum
- **Storage**: Secure cloud storage with public URLs
- **Preview**: Filename and size display after upload

## Maintenance

- **Google Sheets**: Data automatically appends to connected sheet
- **File Storage**: Files stored securely with permanent URLs
- **Error Handling**: Comprehensive error messages and retry logic
- **Validation**: Client and server-side validation

## Support

For technical issues or modifications, refer to the environment setup and ensure all API credentials are properly configured.
