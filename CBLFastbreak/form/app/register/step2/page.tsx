"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, ArrowRight, Plus, Trash2, Users, CreditCard } from "lucide-react"
import Image from "next/image"

interface Player {
  id: string
  fullName: string
  icPassport: string
  email: string
  phone: string
  affiliationType: string
}

export default function Step2() {
  const router = useRouter()
  const [players, setPlayers] = useState<Player[]>([])

  useEffect(() => {
    // Check authentication
    const userAuth = localStorage.getItem("userAuth")
    if (!userAuth) {
      router.push("/")
      return
    }

    // Load saved data
    const savedData = localStorage.getItem("step2Data")
    if (savedData) {
      const data = JSON.parse(savedData)
      setPlayers(data.players || [])
    } else {
      // Add first player by default
      addPlayer()
    }
  }, [router])

  const addPlayer = () => {
    if (players.length < 15) {
      setPlayers([
        ...players,
        {
          id: Date.now().toString(),
          fullName: "",
          icPassport: "",
          email: "",
          phone: "",
          affiliationType: "",
        },
      ])
    }
  }

  const removePlayer = (id: string) => {
    setPlayers(players.filter((player) => player.id !== id))
  }

  const updatePlayer = (id: string, field: keyof Player, value: string) => {
    setPlayers(players.map((player) => (player.id === id ? { ...player, [field]: value } : player)))
  }

  const saveAndContinue = () => {
    const data = { players }
    localStorage.setItem("step2Data", JSON.stringify(data))
    router.push("/register/step3")
  }

  const goBack = () => {
    const data = { players }
    localStorage.setItem("step2Data", JSON.stringify(data))
    router.push("/register/step1")
  }

  const isValid =
    players.length > 0 &&
    players.every(
      (player) =>
        player.fullName.trim() &&
        player.icPassport.trim() &&
        player.email.trim() &&
        player.phone.trim() &&
        player.affiliationType,
    )

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={goBack} className="text-white hover:bg-orange-400">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Step 1
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
              <div className="w-10 h-10 bg-orange-600 rounded-full flex items-center justify-center text-white">
                <Users className="w-5 h-5" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-600">Step 2</p>
                <p className="text-lg font-semibold text-gray-900">Player Roster</p>
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
      <div className="max-w-4xl mx-auto px-6 py-12">
        <Card className="shadow-xl border-0">
          <CardHeader className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-t-lg">
            <CardTitle className="text-2xl flex items-center justify-between">
              <div className="flex items-center">
                <Users className="w-6 h-6 mr-3" />
                Player Roster
              </div>
              <span className="text-lg">({players.length}/15)</span>
            </CardTitle>
            <p className="text-orange-100">Add your team members (minimum 1, maximum 15)</p>
          </CardHeader>
          <CardContent className="p-8 space-y-6">
            {players.map((player, index) => (
              <div key={player.id} className="border rounded-lg p-6 bg-gray-50">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-lg font-semibold text-gray-900">Player {index + 1}</h4>
                  {players.length > 1 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removePlayer(player.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-base font-medium">Full Name *</Label>
                    <Input
                      value={player.fullName}
                      onChange={(e) => updatePlayer(player.id, "fullName", e.target.value)}
                      placeholder="Enter full name"
                      className="mt-1 h-11"
                    />
                  </div>

                  <div>
                    <Label className="text-base font-medium">IC / Passport Number *</Label>
                    <Input
                      value={player.icPassport}
                      onChange={(e) => updatePlayer(player.id, "icPassport", e.target.value)}
                      placeholder="Enter IC or passport number"
                      className="mt-1 h-11"
                    />
                  </div>

                  <div>
                    <Label className="text-base font-medium">Email *</Label>
                    <Input
                      type="email"
                      value={player.email}
                      onChange={(e) => updatePlayer(player.id, "email", e.target.value)}
                      placeholder="Enter email address"
                      className="mt-1 h-11"
                    />
                  </div>

                  <div>
                    <Label className="text-base font-medium">Phone Number *</Label>
                    <Input
                      value={player.phone}
                      onChange={(e) => updatePlayer(player.id, "phone", e.target.value)}
                      placeholder="Enter phone number"
                      className="mt-1 h-11"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <Label className="text-base font-medium">Affiliation Type *</Label>
                    <Select
                      value={player.affiliationType}
                      onValueChange={(value) => updatePlayer(player.id, "affiliationType", value)}
                    >
                      <SelectTrigger className="mt-1 h-11">
                        <SelectValue placeholder="Select affiliation type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Staff">Staff</SelectItem>
                        <SelectItem value="Contract">Contract</SelectItem>
                        <SelectItem value="Intern">Intern</SelectItem>
                        <SelectItem value="Agent">Agent</SelectItem>
                        <SelectItem value="Member">Member</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            ))}

            {players.length < 15 && (
              <Button
                type="button"
                variant="outline"
                onClick={addPlayer}
                className="w-full h-12 border-2 border-dashed border-orange-300 text-orange-600 hover:bg-orange-50 bg-transparent"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add Player ({players.length}/15)
              </Button>
            )}

            <div className="pt-6">
              <Button
                onClick={saveAndContinue}
                disabled={!isValid}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white h-12 text-lg"
              >
                Continue to Payment
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
