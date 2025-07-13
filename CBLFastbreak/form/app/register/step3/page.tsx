"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { ArrowLeft, Upload, FileText, CreditCard, ImageIcon } from "lucide-react"
import Image from "next/image"
import { submitRegistration } from "../../actions"

export default function Step3() {
  const router = useRouter()
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [confirmationChecked, setConfirmationChecked] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    // Check authentication
    const userAuth = localStorage.getItem("userAuth")
    if (!userAuth) {
      router.push("/")
      return
    }

    // Load saved data
    const savedData = localStorage.getItem("step3Data")
    if (savedData) {
      const data = JSON.parse(savedData)
      setConfirmationChecked(data.confirmationChecked || false)
    }
  }, [router])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert("File size must be less than 10MB")
        return
      }

      // Check file type
      const allowedTypes = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
      if (!allowedTypes.includes(file.type)) {
        alert("Only PDF, JPG, and PNG files are allowed")
        return
      }

      setUploadedFile(file)
    }
  }

  const goBack = () => {
    const data = { confirmationChecked }
    localStorage.setItem("step3Data", JSON.stringify(data))
    router.push("/register/step2")
  }

  const handleSubmit = async () => {
    if (!uploadedFile || !confirmationChecked) return

    setIsSubmitting(true)

    try {
      // Get all saved data
      const step1Data = JSON.parse(localStorage.getItem("step1Data") || "{}")
      const step2Data = JSON.parse(localStorage.getItem("step2Data") || "{}")

      // Create form data
      const formData = new FormData()
      formData.append("teamName", step1Data.teamName)
      formData.append("company1", step1Data.company1)
      formData.append("company2", step1Data.company2 || "")
      formData.append("players", JSON.stringify(step2Data.players))
      formData.append("paymentFile", uploadedFile)

      const result = await submitRegistration(formData)

      if (result.success) {
        router.push("/register/confirmation")
      } else {
        alert(result.error || "Submission failed. Please try again.")
      }
    } catch (error) {
      alert("An unexpected error occurred. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const isValid = uploadedFile && confirmationChecked

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={goBack} className="text-white hover:bg-orange-400">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Step 2
            </Button>
            <div className="flex items-center">
              <div className="bg-white p-2 rounded-lg shadow-lg mr-4">
                <Image src="/cbl-logo.jpg" alt="CBL Logo" width={60} height={40} className="object-contain" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">CBL 2025 Corporate Edition</h1>
                <p className="text-orange-100">Team Registration Portal</p>
              </div>
            </div>
            <div className="w-24"></div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                ✓
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Step 1</p>
                <p className="text-lg font-semibold text-gray-900">Team Information</p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                ✓
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Step 2</p>
                <p className="text-lg font-semibold text-gray-900">Player Roster</p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-orange-600 rounded-full flex items-center justify-center text-white">
                <CreditCard className="w-5 h-5" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-600">Step 3</p>
                <p className="text-lg font-semibold text-gray-900">Payment & Submit</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="max-w-2xl mx-auto px-6 py-12">
        <Card className="shadow-xl border-0">
          <CardHeader className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-t-lg">
            <CardTitle className="text-2xl flex items-center">
              <CreditCard className="w-6 h-6 mr-3" />
              Payment & Submission
            </CardTitle>
            <p className="text-orange-100">Upload payment proof and confirm your registration</p>
          </CardHeader>
          <CardContent className="p-8 space-y-6">
            <div>
              <Label className="text-lg font-medium">Payment Proof *</Label>
              <p className="text-sm text-gray-600 mb-4">Upload proof of payment (PDF, JPG, PNG - Max 10MB)</p>
              <div>
                <input
                  id="paymentFile"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById("paymentFile")?.click()}
                  className="w-full h-16 border-2 border-dashed border-orange-300 text-orange-600 hover:bg-orange-50"
                >
                  <Upload className="h-6 w-6 mr-3" />
                  {uploadedFile ? "Change File" : "Upload Payment Proof"}
                </Button>
              </div>

              {uploadedFile && (
                <div className="mt-4 flex items-center space-x-3 p-4 bg-orange-50 rounded-lg border border-orange-200">
                  {uploadedFile.type === "application/pdf" ? (
                    <FileText className="h-8 w-8 text-red-500" />
                  ) : (
                    <ImageIcon className="h-8 w-8 text-blue-500" />
                  )}
                  <div>
                    <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                    <p className="text-sm text-gray-600">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
              )}
            </div>

            <div className="border-t pt-6">
              <div className="flex items-start space-x-3">
                <Checkbox
                  id="confirmation"
                  checked={confirmationChecked}
                  onCheckedChange={(checked) => setConfirmationChecked(checked as boolean)}
                  className="mt-1"
                />
                <Label htmlFor="confirmation" className="text-base leading-relaxed">
                  I confirm that all information provided is accurate and complete. I understand that payment has been
                  made according to the tournament registration requirements.
                </Label>
              </div>
            </div>

            <div className="pt-6">
              <Button
                onClick={handleSubmit}
                disabled={!isValid || isSubmitting}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white h-12 text-lg"
              >
                {isSubmitting ? "Submitting Registration..." : "Submit Registration"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
