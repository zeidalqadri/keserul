"use client"

import type React from "react"

import { useState, useCallback, useRef, useEffect } from "react"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Upload, ExternalLink, Download, Copy, AlertCircle } from "lucide-react"
import Image from "next/image"
import { rv0Api, type ProcessingOptions, type ProcessingResult } from "@/lib/api"

interface ProgressState {
  phase: 1 | 2 | 3 | 4 | 5
  percentage: number
  elapsedTime: number
  estimatedTotal: number
  currentOperation: string
  status: "idle" | "processing" | "complete" | "error" | "paused"
  errorMessage?: string
  jobId?: string
}

interface ColorPalette {
  detectedColors: string[]
  brandColors: string[]
  accuracy: number
}

interface BackendStatus {
  status: "online" | "offline" | "checking"
  version?: string
}

const CORE_PRESETS = [
  {
    id: "color_perfect",
    name: "COLOR PERFECT",
    desc: "LOGO-OPTIMIZED WITH HOLE DETECTION",
    icon: "●",
    recommended: true,
    colors: 16,
    scale: 2.0,
    color: "bauhaus-red",
  },
  {
    id: "default",
    name: "DEFAULT",
    desc: "BALANCED QUALITY/PERFORMANCE",
    icon: "■",
    recommended: false,
    colors: 16,
    scale: 1.0,
    color: "bauhaus-blue",
  },
  {
    id: "high_quality",
    name: "HIGH QUALITY",
    desc: "MAXIMUM DETAIL WITH CUBIC BÉZIER CURVES",
    icon: "▲",
    recommended: false,
    colors: 32,
    scale: 2.0,
    color: "bauhaus-yellow",
  },
  {
    id: "fast",
    name: "FAST",
    desc: "QUICK PROCESSING FOR PREVIEWS",
    icon: "◆",
    recommended: false,
    colors: 8,
    scale: 1.0,
    color: "bauhaus-black",
  },
]

// Bauhaus Geometric Components
const BauhausShape = ({
  type,
  color,
  size = "w-4 h-4",
  className = "",
}: {
  type: "circle" | "square" | "triangle"
  color: string
  size?: string
  className?: string
}) => {
  if (type === "triangle") {
    return <div className={`bauhaus-triangle-${color} ${className}`} />
  }

  return (
    <div
      className={`${size} bauhaus-${color} ${
        type === "circle" ? "bauhaus-shape-circle" : "bauhaus-shape-square"
      } ${className}`}
    />
  )
}

const BauhausDecoration = () => (
  <div className="absolute inset-0 pointer-events-none overflow-hidden">
    <BauhausShape type="circle" color="red" size="w-8 h-8" className="absolute top-20 right-20 bauhaus-float" />
    <BauhausShape type="square" color="blue" size="w-6 h-6" className="absolute top-40 left-10 bauhaus-pulse" />
    <BauhausShape
      type="triangle"
      color="yellow"
      className="absolute bottom-32 right-32 bauhaus-float"
      style={{ animationDelay: "2s" }}
    />
    <BauhausShape
      type="circle"
      color="yellow"
      size="w-4 h-4"
      className="absolute top-60 left-1/3 bauhaus-pulse"
      style={{ animationDelay: "1s" }}
    />
    <BauhausShape
      type="square"
      color="red"
      size="w-5 h-5"
      className="absolute bottom-20 left-20 bauhaus-float"
      style={{ animationDelay: "3s" }}
    />
    <div className="absolute inset-0 bauhaus-grid opacity-30" />
  </div>
)

export default function RV0VectorStudio() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ status: "checking" })
  const [progress, setProgress] = useState<ProgressState>({
    phase: 1,
    percentage: 0,
    elapsedTime: 0,
    estimatedTotal: 0,
    currentOperation: "READY",
    status: "idle",
  })
  const [colorPalette, setColorPalette] = useState<ColorPalette>({
    detectedColors: [],
    brandColors: [],
    accuracy: 100,
  })
  const [selectedPreset, setSelectedPreset] = useState<string>("color_perfect")
  const [colorCount, setColorCount] = useState<number>(16)
  const [scaleMultiplier, setScaleMultiplier] = useState<number>(2.0)
  const [showLogs, setShowLogs] = useState<boolean>(false)
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null)
  const [svgPreview, setSvgPreview] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])

  const fileInputRef = useRef<HTMLInputElement>(null)
  const statusCheckInterval = useRef<NodeJS.Timeout | null>(null)
  const previewRef = useRef<HTMLDivElement>(null)

  // Check backend status on mount
  useEffect(() => {
    checkBackendStatus()
  }, [])

  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`])
  }, [])

  const checkBackendStatus = useCallback(async () => {
    try {
      const status = await rv0Api.checkBackendStatus()
      setBackendStatus(status)
      addLog(`RV0: Backend ${status.status.toUpperCase()}${status.version ? ` (v${status.version})` : ""}`)
    } catch (error) {
      setBackendStatus({ status: "offline" })
      addLog("RV0: Backend connection failed")
    }
  }, [addLog])

  const validateFile = (file: File): string | null => {
    const maxSize = 10 * 1024 * 1024 // 10MB for production
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg", "image/webp"]

    if (!allowedTypes.includes(file.type)) {
      return "UNSUPPORTED FORMAT. USE PNG, JPG, OR WEBP."
    }

    if (file.size > maxSize) {
      return "FILE TOO LARGE. MAX 10MB."
    }

    return null
  }

  const analyzeColors = useCallback(
    async (file: File) => {
      try {
        addLog("RV0: Analyzing image colors...")
        const analysis = await rv0Api.analyzeColors(file)
        setColorPalette({
          detectedColors: analysis.colors,
          brandColors: analysis.colors.slice(0, 2), // Auto-select first 2 as brand colors
          accuracy: analysis.accuracy,
        })
        addLog(`RV0: Detected ${analysis.colors.length} dominant colors (${analysis.accuracy}% accuracy)`)
      } catch (error) {
        addLog(`RV0: Color analysis failed - ${error}`)
        // Fallback to basic colors if API fails
        const fallbackColors = ["#e53e3e", "#3182ce", "#d69e2e", "#1a1a1a", "#ffffff"]
        setColorPalette({
          detectedColors: fallbackColors,
          brandColors: fallbackColors.slice(0, 2),
          accuracy: 85,
        })
      }
    },
    [addLog],
  )

  const handleFileUpload = useCallback(
    async (file: File) => {
      const error = validateFile(file)
      if (error) {
        setProgress((prev) => ({ ...prev, status: "error", errorMessage: error }))
        return
      }

      setUploadedFile(file)
      setProgress((prev) => ({ ...prev, status: "idle", errorMessage: undefined }))
      addLog(`RV0: Image loaded - ${file.name} (${Math.round(file.size / 1024)}KB)`)

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)

      // Analyze colors
      await analyzeColors(file)
    },
    [addLog, analyzeColors],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        handleFileUpload(files[0])
      }
    },
    [handleFileUpload],
  )

  const pollProcessingStatus = useCallback(
    async (jobId: string) => {
      const startTime = Date.now()

      const poll = async () => {
        try {
          const status = await rv0Api.getProcessingStatus(jobId)
          const elapsed = Date.now() - startTime

          setProgress((prev) => ({
            ...prev,
            phase: status.phase as any,
            percentage: status.percentage,
            elapsedTime: elapsed,
            estimatedTotal: status.estimatedTotal || 0,
            currentOperation: status.currentOperation,
            status: status.status === "complete" ? "complete" : status.status === "error" ? "error" : "processing",
            errorMessage: status.error,
          }))

          addLog(`RV0: ${status.currentOperation} (${status.percentage}%)`)

          if (status.status === "complete") {
            // Get final result
            const result = await rv0Api.getResult(jobId)
            setProcessingResult(result)

            if (result.svgContent) {
              setSvgPreview(result.svgContent)
            }

            addLog(
              `RV0: ✓ Processing complete - ${result.metrics?.pathCount} paths, ${result.metrics?.colorCount} colors`,
            )

            if (statusCheckInterval.current) {
              clearInterval(statusCheckInterval.current)
            }
          } else if (status.status === "error") {
            addLog(`RV0: ✗ Processing failed - ${status.error}`)
            if (statusCheckInterval.current) {
              clearInterval(statusCheckInterval.current)
            }
          }
        } catch (error) {
          addLog(`RV0: Status check failed - ${error}`)
          setProgress((prev) => ({
            ...prev,
            status: "error",
            errorMessage: `Connection lost: ${error}`,
          }))
          if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current)
          }
        }
      }

      // Poll every 1 second
      statusCheckInterval.current = setInterval(poll, 1000)
      poll() // Initial check
    },
    [addLog],
  )

  const startProcessing = useCallback(async () => {
    if (!uploadedFile || backendStatus.status !== "online") {
      setProgress((prev) => ({
        ...prev,
        status: "error",
        errorMessage: "Backend offline or no file selected",
      }))
      return
    }

    try {
      setProgress((prev) => ({ ...prev, status: "processing", percentage: 0 }))
      setProcessingResult(null)
      setSvgPreview(null)

      addLog("RV0: Starting vectorization...")

      const options: ProcessingOptions = {
        preset: selectedPreset,
        colors: colorCount,
        scale: scaleMultiplier,
        brandColors: colorPalette.brandColors.length > 0 ? colorPalette.brandColors : undefined,
      }

      const { jobId } = await rv0Api.uploadAndProcess(uploadedFile, options)

      setProgress((prev) => ({ ...prev, jobId }))
      addLog(`RV0: Job queued - ID: ${jobId}`)

      // Start polling for status
      await pollProcessingStatus(jobId)
    } catch (error) {
      addLog(`RV0: Upload failed - ${error}`)
      setProgress((prev) => ({
        ...prev,
        status: "error",
        errorMessage: `Upload failed: ${error}`,
      }))
    }
  }, [
    uploadedFile,
    backendStatus.status,
    selectedPreset,
    colorCount,
    scaleMultiplier,
    colorPalette.brandColors,
    addLog,
    pollProcessingStatus,
  ])

  const downloadSvg = useCallback(async () => {
    if (!progress.jobId) return

    try {
      addLog("RV0: Downloading SVG...")
      const blob = await rv0Api.downloadSvg(progress.jobId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${uploadedFile?.name.replace(/\.[^/.]+$/, "") || "vectorized"}.svg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      addLog("RV0: ✓ Download complete")
    } catch (error) {
      addLog(`RV0: Download failed - ${error}`)
    }
  }, [progress.jobId, uploadedFile?.name, addLog])

  const generateCommand = useCallback(() => {
    if (!uploadedFile) return "# Upload a file to generate API command"

    const options: ProcessingOptions = {
      preset: selectedPreset,
      colors: colorCount,
      scale: scaleMultiplier,
      brandColors: colorPalette.brandColors.length > 0 ? colorPalette.brandColors : undefined,
    }

    return rv0Api.generateCurlCommand(uploadedFile, options)
  }, [uploadedFile, selectedPreset, colorCount, scaleMultiplier, colorPalette.brandColors])

  const copyCommand = useCallback(() => {
    navigator.clipboard.writeText(generateCommand())
    addLog("RV0: Command copied to clipboard")
  }, [generateCommand, addLog])

  const openApiDocs = useCallback(() => {
    window.open(rv0Api.getApiDocumentation(), "_blank")
  }, [])

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    return minutes > 0 ? `${minutes}M ${seconds % 60}S` : `${seconds}S`
  }

  // Auto-scroll to preview on completion
  useEffect(() => {
    if (progress.status === "complete" && previewRef.current) {
      previewRef.current.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }, [progress.status])

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current)
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-bauhaus-gray font-bauhaus relative flex flex-col">
      <BauhausDecoration />

      <div className="mx-auto px-4 py-4 relative z-10 flex flex-col h-screen w-full">
        {/* Header */}
        <div className="bauhaus-card p-3 relative mb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bauhaus-logo-container">
                <Image src="/rv0-logo.png" alt="rv0" width={100} height={40} className="h-10 w-auto" priority />
              </div>
              <div>
                <h1 className="bauhaus-title text-2xl text-bauhaus-black">VECTOR STUDIO</h1>
                <p className="text-xs text-bauhaus-black opacity-70">PRODUCTION API INTEGRATION</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`flex items-center gap-2 px-3 py-1 ${
                  backendStatus.status === "online"
                    ? "bg-bauhaus-black text-white"
                    : backendStatus.status === "offline"
                      ? "bg-bauhaus-red text-white"
                      : "bg-bauhaus-yellow text-bauhaus-black"
                }`}
              >
                <BauhausShape
                  type="circle"
                  color={backendStatus.status === "online" ? "white" : "white"}
                  size="w-2 h-2"
                />
                <span className="text-xs font-bold">
                  {backendStatus.status.toUpperCase()}
                  {backendStatus.version && ` v${backendStatus.version}`}
                </span>
              </div>
              <button className="bauhaus-button text-xs" onClick={openApiDocs} title="Open API documentation">
                <ExternalLink className="w-3 h-3" />
                API
              </button>
            </div>
          </div>
          <BauhausShape type="square" color="red" size="w-4 h-4" className="absolute top-3 right-3" />
        </div>
        {/* Backend Offline Warning */}
        {backendStatus.status === "offline" && (
          <div className="bauhaus-card bg-bauhaus-red text-white p-4 mb-3">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5" />
              <div>
                <div className="font-bold">BACKEND OFFLINE</div>
                <div className="text-xs opacity-90">
                  Cannot connect to production API. Check network connection or try again later.
                </div>
              </div>
              <button className="bauhaus-button text-xs ml-auto" onClick={checkBackendStatus}>
                RETRY
              </button>
            </div>
          </div>
        )}
        {/* Main Input Area - This will be scrollable if content exceeds height */}
        <div className="flex-grow overflow-y-auto pr-2">
          {/* Upload */}
          <div
            className="bauhaus-upload bauhaus-card p-4 text-center relative cursor-pointer mb-3"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            title="Drag & drop images here or click to browse. Supports PNG, JPG, WEBP. Max 10MB."
          >
            <div className="w-12 h-12 bg-bauhaus-black mx-auto mb-3 flex items-center justify-center">
              <Upload className="h-6 w-6 text-white" />
            </div>
            <h3 className="bauhaus-title text-lg text-bauhaus-black mb-2">
              {uploadedFile ? `✓ ${uploadedFile.name}` : "UPLOAD IMAGE"}
            </h3>
            {uploadedFile && (
              <div className="text-xs text-bauhaus-black opacity-70">{Math.round(uploadedFile.size / 1024)}KB</div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFileUpload(file)
              }}
            />
          </div>

          {/* Error */}
          {progress.status === "error" && progress.errorMessage && (
            <div className="bauhaus-card bg-bauhaus-red text-white p-2 mb-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span className="font-bold">{progress.errorMessage}</span>
              </div>
            </div>
          )}

          {/* Progress */}
          {progress.status !== "idle" && progress.status !== "error" && (
            <div className="bauhaus-card p-3 mb-3">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="bauhaus-title text-sm">
                    PROGRESS {progress.jobId && `(${progress.jobId.slice(0, 8)}...)`}
                  </span>
                  <span className="text-xs">
                    {progress.percentage.toFixed(0)}% | {formatTime(progress.elapsedTime)}
                    {progress.estimatedTotal > 0 && ` / ~${formatTime(progress.estimatedTotal)}`}
                  </span>
                </div>

                <div className="relative">
                  <div className="h-6 bg-bauhaus-gray border-2 border-bauhaus-black relative overflow-hidden">
                    <div
                      className="h-full bauhaus-progress transition-all duration-300"
                      style={{ width: `${progress.percentage}%` }}
                    ></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xs text-bauhaus-black font-bold mix-blend-difference">
                        PHASE {progress.phase}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-xs text-bauhaus-black">{progress.currentOperation}</div>

                <button
                  className="bauhaus-button text-xs"
                  onClick={() => setShowLogs(!showLogs)}
                  title="Toggle processing logs"
                >
                  {showLogs ? "HIDE" : "SHOW"} LOG
                </button>

                {showLogs && (
                  <div className="bg-bauhaus-black text-white p-3 font-mono text-xs space-y-1 max-h-32 overflow-y-auto">
                    {logs.slice(-10).map((log, i) => (
                      <div key={i} className={log.includes("✓") ? "text-bauhaus-yellow" : ""}>
                        {log}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Colors */}
          {colorPalette.detectedColors.length > 0 && (
            <div className="bauhaus-card p-3 relative mb-3">
              <h3 className="bauhaus-title text-sm mb-4">COLORS ({colorPalette.accuracy}% LAB ACCURACY)</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-xs block mb-2" title="Auto-detected dominant colors from your image">
                    DETECTED:
                  </label>
                  <div className="flex gap-2">
                    {colorPalette.detectedColors.map((color, i) => (
                      <div
                        key={i}
                        className="w-8 h-8 border-2 border-bauhaus-black cursor-pointer"
                        style={{ backgroundColor: color }}
                        title={`${color} - Click to add to brand palette`}
                        onClick={() => {
                          if (!colorPalette.brandColors.includes(color)) {
                            setColorPalette((prev) => ({
                              ...prev,
                              brandColors: [...prev.brandColors, color],
                            }))
                          }
                        }}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs block mb-2" title="Your brand colors for consistent output">
                    BRAND:
                  </label>
                  <div className="flex gap-2 items-center">
                    {colorPalette.brandColors.map((color, i) => (
                      <Input
                        key={i}
                        type="color"
                        value={color}
                        onChange={(e) => {
                          const newColors = [...colorPalette.brandColors]
                          newColors[i] = e.target.value
                          setColorPalette((prev) => ({ ...prev, brandColors: newColors }))
                        }}
                        className="w-8 h-8 p-0 border-2 border-bauhaus-black cursor-pointer"
                        title={`Brand color ${i + 1}: ${color}`}
                      />
                    ))}
                    <button
                      className="bauhaus-button text-xs"
                      onClick={() => {
                        setColorPalette((prev) => ({
                          ...prev,
                          brandColors: [...prev.brandColors, "#1a1a1a"],
                        }))
                      }}
                      title="Add new brand color"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Presets */}
          <div className="bauhaus-card p-3 mb-3">
            <h3 className="bauhaus-title text-sm mb-2">PRESETS</h3>
            <div className="grid grid-cols-2 gap-3">
              {CORE_PRESETS.map((preset) => (
                <div
                  key={preset.id}
                  className={`p-3 border-3 cursor-pointer transition-all relative ${
                    selectedPreset === preset.id
                      ? "border-bauhaus-black bg-white"
                      : "border-gray-400 bg-bauhaus-gray hover:border-bauhaus-black"
                  }`}
                  onClick={() => {
                    setSelectedPreset(preset.id)
                    setColorCount(preset.colors)
                    setScaleMultiplier(preset.scale)
                  }}
                  title={preset.desc}
                >
                  {preset.recommended && (
                    <div className="absolute -top-2 -right-2 bg-bauhaus-red text-white px-1 py-0.5 text-xs font-bold">
                      ★
                    </div>
                  )}

                  <div className="flex items-center gap-2 mb-1">
                    <div
                      className={`w-5 h-5 bg-${preset.color} flex items-center justify-center text-white text-xs font-bold`}
                    >
                      {preset.icon}
                    </div>
                    <h4 className="bauhaus-title text-xs">{preset.name}</h4>
                  </div>

                  <div className="text-xs text-bauhaus-black opacity-70">
                    {preset.colors}C • {preset.scale}X
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Parameters */}
          <div className="bauhaus-card p-3 mb-3">
            <h3 className="bauhaus-title text-sm mb-2">PARAMETERS</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  className="text-xs block mb-1"
                  title="Number of colors in output. More colors = higher quality but slower processing"
                >
                  COLORS: {colorCount}
                </label>
                <Slider
                  value={[colorCount]}
                  onValueChange={(value) => setColorCount(value[0])}
                  min={8}
                  max={32}
                  step={1}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-xs block mb-1" title="Output size multiplier for high-resolution exports">
                  SCALE: {scaleMultiplier}X
                </label>
                <Slider
                  value={[scaleMultiplier]}
                  onValueChange={(value) => setScaleMultiplier(value[0])}
                  min={1.0}
                  max={4.0}
                  step={0.1}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </div>{" "}
        {/* End of main input area wrapper */}
        {/* Preview & Command - These will be scrolled to */}
        <div ref={previewRef} className="mt-auto pt-4">
          {uploadedFile && (
            <div className="bauhaus-card p-3 mb-3">
              <h3 className="bauhaus-title text-sm mb-2">PREVIEW</h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <h4 className="text-xs mb-2">ORIGINAL</h4>
                  <div className="aspect-square bg-bauhaus-gray border-2 border-bauhaus-black flex items-center justify-center overflow-hidden">
                    {imagePreview ? (
                      <img
                        src={imagePreview || "/placeholder.svg"}
                        alt="Original"
                        className="max-w-full max-h-full object-contain"
                      />
                    ) : (
                      <span className="text-xs">LOADING...</span>
                    )}
                  </div>
                </div>

                <div className="text-center">
                  <h4 className="text-xs mb-2">VECTORIZED</h4>
                  <div className="aspect-square bg-bauhaus-gray border-2 border-bauhaus-black flex items-center justify-center">
                    {svgPreview ? (
                      <div dangerouslySetInnerHTML={{ __html: svgPreview }} className="w-full h-full" />
                    ) : progress.status === "complete" ? (
                      <span className="text-xs text-bauhaus-blue">✓ READY</span>
                    ) : (
                      <span className="text-xs">PROCESSING...</span>
                    )}
                  </div>
                </div>

                <div className="text-center">
                  <h4 className="text-xs mb-2">METRICS</h4>
                  {processingResult?.metrics ? (
                    <div className="text-left space-y-1 text-xs">
                      <div>TIME: {formatTime(processingResult.metrics.processingTime)}</div>
                      <div>PATHS: {processingResult.metrics.pathCount}</div>
                      <div>COLORS: {processingResult.metrics.colorCount}</div>
                      <div>REDUCTION: {processingResult.metrics.sizeReduction}%</div>
                      <div className="text-bauhaus-blue">
                        {Math.round(processingResult.metrics.originalSize / 1024)}KB →{" "}
                        {Math.round(processingResult.metrics.outputSize / 1024)}KB
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-bauhaus-black opacity-70">PENDING</div>
                  )}
                </div>
              </div>

              {(progress.status === "idle" || progress.status === "complete") &&
                uploadedFile &&
                backendStatus.status === "online" && (
                  <div className="mt-4 text-center">
                    <button
                      onClick={startProcessing}
                      className="bauhaus-button bauhaus-button-red text-sm px-6 py-2"
                      title={
                        progress.status === "complete"
                          ? "Re-vectorize with current settings"
                          : "Start vectorization with current settings"
                      }
                      disabled={progress.status === "processing"}
                    >
                      {progress.status === "complete" ? "RE-VECTORIZE" : "START VECTORIZATION"}
                    </button>
                  </div>
                )}
            </div>
          )}

          {/* Command & Export */}
          <div className="bauhaus-card p-3">
            <h3 className="bauhaus-title text-sm mb-2">API COMMAND</h3>
            <div className="bg-bauhaus-black text-white p-2 font-mono text-xs overflow-x-auto mb-2">
              <pre>{generateCommand()}</pre>
            </div>
            <div className="flex gap-2 flex-wrap">
              <button className="bauhaus-button text-xs" onClick={copyCommand} title="Copy cURL command to clipboard">
                <Copy className="w-3 h-3" />
                COPY
              </button>
              <button
                className="bauhaus-button bauhaus-button-blue text-xs"
                disabled={!processingResult?.success}
                onClick={downloadSvg}
                title="Download vectorized SVG file"
              >
                <Download className="w-3 h-3" />
                DOWNLOAD
              </button>
              <button
                className="bauhaus-button bauhaus-button-yellow text-xs"
                onClick={openApiDocs}
                title="Open API documentation"
              >
                <ExternalLink className="w-3 h-3" />
                DOCS
              </button>
            </div>

            {processingResult?.success && (
              <div className="bg-bauhaus-yellow text-bauhaus-black p-2 mt-3 relative">
                <BauhausShape type="square" color="red" size="w-3 h-3" className="absolute top-1 right-1" />
                <div className="text-sm font-bold">✓ VECTORIZATION COMPLETE!</div>
                <div className="text-xs mt-0.5">
                  Job ID: {progress.jobId} | Output: {processingResult.outputPath || "Ready for download"}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
