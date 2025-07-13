"use server"

import { google } from "googleapis"

interface UserFormData {
  email: string
  step1?: any
  step2?: any
  step3?: any
  lastUpdated: string
}

// Get user form data from Google Sheets
export async function getUserFormData(email: string): Promise<UserFormData | null> {
  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
      },
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    })

    const sheets = google.sheets({ version: "v4", auth })
    const spreadsheetId = process.env.GOOGLE_SHEET_ID

    // Check if user data sheet exists, if not create it
    const response = await sheets.spreadsheets.values
      .get({
        spreadsheetId,
        range: "UserData!A:E",
      })
      .catch(() => null)

    if (!response) {
      // Create UserData sheet
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: {
          requests: [
            {
              addSheet: {
                properties: {
                  title: "UserData",
                },
              },
            },
          ],
        },
      })

      // Add headers
      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range: "UserData!A1:E1",
        valueInputOption: "USER_ENTERED",
        requestBody: {
          values: [["Email", "Step1Data", "Step2Data", "Step3Data", "LastUpdated"]],
        },
      })

      return null
    }

    const rows = response.data.values || []
    const userRow = rows.find((row) => row[0] === email)

    if (!userRow) return null

    return {
      email: userRow[0],
      step1: userRow[1] ? JSON.parse(userRow[1]) : null,
      step2: userRow[2] ? JSON.parse(userRow[2]) : null,
      step3: userRow[3] ? JSON.parse(userRow[3]) : null,
      lastUpdated: userRow[4] || "",
    }
  } catch (error) {
    console.error("Error getting user data:", error)
    return null
  }
}

// Save user form data to Google Sheets
export async function saveUserFormData(email: string, step: string, data: any) {
  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
      },
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    })

    const sheets = google.sheets({ version: "v4", auth })
    const spreadsheetId = process.env.GOOGLE_SHEET_ID

    // Get existing user data
    const existingData = await getUserFormData(email)
    const timestamp = new Date().toISOString()

    let userData: UserFormData = {
      email,
      lastUpdated: timestamp,
    }

    if (existingData) {
      userData = { ...existingData, lastUpdated: timestamp }
    }

    // Update the specific step
    userData[step as keyof UserFormData] = data

    // Find the row to update or create new row
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: "UserData!A:E",
    })

    const rows = response.data.values || []
    const userRowIndex = rows.findIndex((row) => row[0] === email)

    const rowData = [
      email,
      JSON.stringify(userData.step1 || {}),
      JSON.stringify(userData.step2 || {}),
      JSON.stringify(userData.step3 || {}),
      timestamp,
    ]

    if (userRowIndex > 0) {
      // Update existing row
      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range: `UserData!A${userRowIndex + 1}:E${userRowIndex + 1}`,
        valueInputOption: "USER_ENTERED",
        requestBody: {
          values: [rowData],
        },
      })
    } else {
      // Append new row
      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range: "UserData!A:E",
        valueInputOption: "USER_ENTERED",
        requestBody: {
          values: [rowData],
        },
      })
    }
  } catch (error) {
    console.error("Error saving user data:", error)
    throw error
  }
}
