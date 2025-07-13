"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Edit, Home, FileText, Users, CreditCard } from "lucide-react"
import Image from "next/image"

export default function Confirmation() {
  const router = useRouter()
  const [registrationData, setRegistrationData] = useState<any>(null)

  useEffect(() => {
    // Check authentication
    const userAuth = localStorage.getItem("userAuth")
    if (!userAuth) {
      router.push("/")
      return
    }

    // Load all registration data
    const step1Data = JSON.parse(localStorage.getItem("step1Data") || "{}")
    const step2Data = JSON.parse(localStorage.getItem("step2Data") || "{}")
    const step3Data = JSON.parse(localStorage.getItem("step3Data") || "{}")

    setRegistrationData({
      step1: step1Data,
      step2: step2Data,
      step3: step3Data,
    })
  }, [router])

  const handleEditStep = (step: number) => {
    router.push(`/register/step${step}`)
  }

  const handleNewRegistration = () => {
    // Clear all data and start fresh
    localStorage.removeItem("step1Data")
    localStorage.removeItem("step2Data")
    localStorage.removeItem("step3Data")
    router.push("/register/step1")
  }

  const handleGoHome = () => {
    router.push("/")
  }

  if (!registrationData) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-center">
            <div className="flex items-center">
              <div className="bg-white p-2 rounded-lg shadow-lg mr-4">
                <Image src="/cbl-logo.jpg" alt="CBL Logo" width={60} height={40} className="object-contain" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">CBL 2025 Corporate Edition</h1>
                <p className="text-orange-100">Team Registration Portal</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Success Message */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <Card className="shadow-xl border-0 mb-8">
          <CardContent className="p-12 text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Registration Successful!</h2>
            <p className="text-lg text-gray-600 mb-8">
              Your team registration for CBL 2025 has been submitted successfully. You will receive a confirmation email
              shortly.
            </p>
            <div className="flex justify-center space-x-4">
              <Button onClick={handleGoHome} className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3">
                <Home className="w-5 h-5 mr-2" />
                Go to Home
              </Button>
              <Button onClick={handleNewRegistration} variant="outline" className="px-8 py-3 bg-transparent">
                Register Another Team
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Registration Summary */}
        <div className="grid gap-6">
          {/* Team Information */}
          <Card className="shadow-lg border-0">
            <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Team Information
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditStep(1)}
                  className="text-white hover:bg-green-400"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Team Name</p>
                  <p className="font-semibold">{registrationData.step1.teamName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Company</p>
                  <p className="font-semibold">{registrationData.step1.company1}</p>
                </div>
                {registrationData.step1.company2 && (
                  <div>
                    <p className="text-sm text-gray-600">Second Company</p>
                    <p className="font-semibold">{registrationData.step1.company2}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Player Roster */}
          <Card className="shadow-lg border-0">
            <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Player Roster ({registrationData.step2.players?.length || 0} players)
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditStep(2)}
                  className="text-white hover:bg-green-400"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                {registrationData.step2.players?.map((player: any, index: number) => (
                  <div key={player.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Player {index + 1}</p>
                        <p className="font-semibold">{player.fullName}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Email</p>
                        <p className="font-semibold">{player.email}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Affiliation</p>
                        <p className="font-semibold">{player.affiliationType}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Payment Confirmation */}
          <Card className="shadow-lg border-0">
            <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  Payment & Submission
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditStep(3)}
                  className="text-white hover:bg-green-400"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <p className="font-semibold">Payment proof uploaded</p>
                  <p className="text-sm text-gray-600">Registration confirmed and submitted</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
