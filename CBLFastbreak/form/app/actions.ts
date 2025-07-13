"use server"

import { google } from "googleapis"
import { put } from "@vercel/blob"

interface Player {
  id: string
  fullName: string
  icPassport: string
  email: string
  phone: string
  affiliationType: string
}

export async function submitRegistration(formData: FormData) {
  try {
    console.log("Starting form submission...")

    // Extract form data
    const teamName = formData.get("teamName") as string
    const company1 = formData.get("company1") as string
    const company2 = formData.get("company2") as string
    const playersJson = formData.get("players") as string
    const paymentFile = formData.get("paymentFile") as File

    console.log("Form data extracted:", {
      teamName,
      company1,
      company2,
      playersCount: playersJson ? JSON.parse(playersJson).length : 0,
    })

    // Validate required environment variables
    if (!process.env.GOOGLE_CLIENT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY || !process.env.GOOGLE_SHEET_ID) {
      console.error("Missing Google Sheets environment variables")
      return { success: false, error: "Google Sheets configuration missing" }
    }

    const players: Player[] = JSON.parse(playersJson)

    // Upload file to Vercel Blob
    let fileUrl = ""
    if (paymentFile && paymentFile.size > 0) {
      console.log("Uploading file:", paymentFile.name, paymentFile.size)
      try {
        const blob = await put(paymentFile.name, paymentFile, {
          access: "public",
          addRandomSuffix: true,
        })
        fileUrl = blob.url
        console.log("File uploaded successfully:", fileUrl)
      } catch (uploadError) {
        console.error("File upload error:", uploadError)
        return { success: false, error: "Failed to upload payment file" }
      }
    }

    // Prepare data for Google Sheets
    const timestamp = new Date().toISOString()
    const playersList = players
      .map((p) => `${p.fullName} (${p.icPassport}) - ${p.email} - ${p.phone} - ${p.affiliationType}`)
      .join("; ")

    console.log("Prepared data for Google Sheets")

    // Google Sheets integration
    await appendToGoogleSheet({
      timestamp,
      teamName,
      company1,
      company2: company2 || "",
      playersList,
      paymentFileUrl: fileUrl,
    })

    console.log("Successfully submitted to Google Sheets")
    return { success: true }
  } catch (error) {
    console.error("Submission error:", error)
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to submit registration",
    }
  }
}

async function appendToGoogleSheet(data: {
  timestamp: string
  teamName: string
  company1: string
  company2: string
  playersList: string
  paymentFileUrl: string
}) {
  try {
    console.log("Initializing Google Sheets API...")

    // Initialize Google Sheets API
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
      },
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    })

    const sheets = google.sheets({ version: "v4", auth })
    const spreadsheetId = process.env.GOOGLE_SHEET_ID

    console.log("Appending data to sheet:", spreadsheetId)

    // Append data to sheet
    const response = await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: "Sheet1!A:F",
      valueInputOption: "USER_ENTERED",
      requestBody: {
        values: [[data.timestamp, data.teamName, data.company1, data.company2, data.playersList, data.paymentFileUrl]],
      },
    })

    console.log("Data successfully appended to Google Sheet:", response.data)
  } catch (error) {
    console.error("Google Sheets error:", error)
    throw new Error(`Google Sheets integration failed: ${error instanceof Error ? error.message : "Unknown error"}`)
  }
}
