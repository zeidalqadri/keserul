"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { ArrowLeft, ArrowRight, FileText, Users, CreditCard, Loader2 } from "lucide-react"
import Image from "next/image"
import { getUserFormData, saveUserFormData } from "../../lib/userData"

export default function Step1() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [teamName, setTeamName] = useState("")
  const [company1, setCompany1] = useState("")
  const [hasSecondCompany, setHasSecondCompany] = useState(false)
  const [company2, setCompany2] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (status === "loading") return

    if (!session) {
      router.push("/")
      return
    }

    // Load saved data for this user
    const loadUserData = async () => {
      try {
        const userData = await getUserFormData(session.user?.email!)
        if (userData?.step1) {
          const data = userData.step1
          setTeamName(data.teamName || "")
          setCompany1(data.company1 || "")
          setHasSecondCompany(data.hasSecondCompany || false)
          setCompany2(data.company2 || "")
        }
      } catch (error) {
        console.error("Error loading user data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadUserData()
  }, [session, status, router])

  const saveAndContinue = async () => {
    if (!session?.user?.email) return

    const data = {
      teamName,
      company1,
      hasSecondCompany,
      company2,
    }

    try {
      await saveUserFormData(session.user.email, "step1", data)
      router.push("/register/step2")
    } catch (error) {
      console.error("Error saving data:", error)
      alert("Error saving data. Please try again.")
    }
  }

  const isValid = teamName.trim() && company1.trim() && (!hasSecondCompany || company2.trim())

  if (status === "loading" || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-orange-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={() => router.push("/")} className="text-white hover:bg-orange-400">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
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
            <div className="flex items-center">
              {session.user?.image && (
                <Image
                  src={session.user.image || "/placeholder.svg"}
                  alt="Profile"
                  width={32}
                  height={32}
                  className="rounded-full mr-2"
                />
              )}
              <span className="text-sm text-orange-100">{session.user?.name}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-orange-600 rounded-full flex items-center justify-center text-white font-semibold">
                <FileText className="w-5 h-5" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-600">Step 1</p>
                <p className="text-lg font-semibold text-gray-900">Team Information</p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-gray-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-400">Step 2</p>
                <p className="text-lg text-gray-400">Player Roster</p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-gray-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-400">Step 3</p>
                <p className="text-lg text-gray-400">Payment & Submit</p>
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
              <FileText className="w-6 h-6 mr-3" />
              Team Information
            </CardTitle>
            <p className="text-orange-100">Tell us about your team and company</p>
          </CardHeader>
          <CardContent className="p-8 space-y-6">
            <div>
              <Label htmlFor="teamName" className="text-lg font-medium">
                Team Name *
              </Label>
              <Input
                id="teamName"
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
                placeholder="Enter your team name"
                className="mt-2 h-12 text-lg"
                required
              />
            </div>

            <div>
              <Label htmlFor="company1" className="text-lg font-medium">
                Company Name *
              </Label>
              <Input
                id="company1"
                value={company1}
                onChange={(e) => setCompany1(e.target.value)}
                placeholder="Enter your company name"
                className="mt-2 h-12 text-lg"
                required
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="secondCompany"
                  checked={hasSecondCompany}
                  onCheckedChange={(checked) => {
                    setHasSecondCompany(checked as boolean)
                    if (!checked) setCompany2("")
                  }}
                />
                <Label htmlFor="secondCompany" className="text-base">
                  Add second company (for SME partnerships - companies with {"<"}50 employees)
                </Label>
              </div>

              {hasSecondCompany && (
                <div>
                  <Label htmlFor="company2" className="text-lg font-medium">
                    Second Company Name *
                  </Label>
                  <Input
                    id="company2"
                    value={company2}
                    onChange={(e) => setCompany2(e.target.value)}
                    placeholder="Enter second company name"
                    className="mt-2 h-12 text-lg"
                  />
                </div>
              )}
            </div>

            <div className="pt-6">
              <Button
                onClick={saveAndContinue}
                disabled={!isValid}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white h-12 text-lg"
              >
                Continue to Player Roster
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
