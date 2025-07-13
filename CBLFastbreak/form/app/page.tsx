"use client"

import { useSession, signIn, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { LogIn, Users, FileText, CreditCard, Loader2 } from "lucide-react"
import Image from "next/image"

export default function HomePage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    try {
      await signIn("google", { callbackUrl: "/register/step1" })
    } catch (error) {
      console.error("Sign in error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleContinueRegistration = () => {
    router.push("/register/step1")
  }

  const handleSignOut = async () => {
    await signOut({ callbackUrl: "/" })
  }

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-orange-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-white p-4 rounded-lg shadow-lg">
              <Image src="/cbl-logo.jpg" alt="CBL Logo" width={120} height={80} className="object-contain" />
            </div>
          </div>
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2">CBL 2025 Corporate Edition</h1>
            <p className="text-xl text-orange-100">Team Registration Portal</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        {!session ? (
          <Card className="shadow-xl border-0">
            <CardContent className="p-12 text-center">
              <div className="mb-8">
                <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <LogIn className="w-10 h-10 text-orange-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to CBL 2025 Corporate Edition</h2>
                <p className="text-lg text-gray-600 mb-8">
                  Sign in with Google to register your team for the Corporate Basketball League tournament. Your
                  progress will be saved automatically.
                </p>
              </div>

              <button
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                className="flex items-center justify-center px-6 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 mr-3 animate-spin" />
                ) : (
                  <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                )}
                {isLoading ? "Signing in..." : "Sign in with Google"}
              </button>

              <div className="mt-8 text-sm text-gray-500">
                <p>Secure authentication • Progress auto-saved • Easy team management</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-8">
            {/* Welcome Back */}
            <Card className="shadow-xl border-0">
              <CardContent className="p-8">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center">
                    {session.user?.image && (
                      <Image
                        src={session.user.image || "/placeholder.svg"}
                        alt="Profile"
                        width={48}
                        height={48}
                        className="rounded-full mr-4"
                      />
                    )}
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        Welcome back, {session.user?.name || session.user?.email}!
                      </h2>
                      <p className="text-gray-600">Continue your team registration</p>
                    </div>
                  </div>
                  <Button variant="outline" onClick={handleSignOut}>
                    Sign Out
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Registration Steps */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="shadow-lg border-0 hover:shadow-xl transition-shadow cursor-pointer group">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-orange-200 transition-colors">
                    <FileText className="w-8 h-8 text-orange-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Step 1</h3>
                  <p className="text-gray-600 mb-4">Team Information</p>
                  <p className="text-sm text-gray-500">Company details and team setup</p>
                </CardContent>
              </Card>

              <Card className="shadow-lg border-0 hover:shadow-xl transition-shadow cursor-pointer group">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
                    <Users className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Step 2</h3>
                  <p className="text-gray-600 mb-4">Player Roster</p>
                  <p className="text-sm text-gray-500">Add up to 15 team members</p>
                </CardContent>
              </Card>

              <Card className="shadow-lg border-0 hover:shadow-xl transition-shadow cursor-pointer group">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
                    <CreditCard className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Step 3</h3>
                  <p className="text-gray-600 mb-4">Payment & Submit</p>
                  <p className="text-sm text-gray-500">Upload payment proof and confirm</p>
                </CardContent>
              </Card>
            </div>

            {/* Continue Button */}
            <div className="text-center">
              <Button
                onClick={handleContinueRegistration}
                size="lg"
                className="bg-orange-600 hover:bg-orange-700 text-white px-12 py-4 text-lg"
              >
                Start Registration
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
