"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Upload } from "lucide-react"
import Image from "next/image"

interface ProgressState {
  phase: 1 | 2 | 3 | 4 | 5
  percentage: number
  elapsedTime: number
  estimatedTotal: number
  currentOperation: string
  status: "idle" | "processing" | "complete" | "error" | "paused"
  errorMessage?: string
}

interface ColorPalette {
  detectedColors: string[]
  brandColors: string[]
  accuracy: number
}

interface ProcessingResult {
  success: boolean
  outputPath?: string
  svgContent?: string
  metrics?: {
    processingTime: number
    pathCount: number
    colorCount: number
    sizeReduction: number
  }
  error?: string
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

const PROCESSING_PHASES = {
  1: { name: "IMAGE ANALYSIS", range: [0, 20] },
  2: { name: "COLOR QUANTIZATION", range: [20, 40] },
  3: { name: "HOLE DETECTION", range: [40, 70] },
  4: { name: "PATH GENERATION", range: [70, 90] },
  5: { name: "SVG EXPORT", range: [90, 100] },
}

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

  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    const maxSize = 2 * 1024 * 1024
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg"]

    if (!allowedTypes.includes(file.type)) {
      return "UNSUPPORTED FORMAT. USE PNG OR JPG."
    }

    if (file.size > maxSize) {
      return "FILE TOO LARGE. MAX 2MB."
    }

    return null
  }

  const handleFileUpload = useCallback((file: File) => {
    const error = validateFile(file)
    if (error) {
      setProgress((prev) => ({ ...prev, status: "error", errorMessage: error }))
      return
    }

    setUploadedFile(file)
    setProgress((prev) => ({ ...prev, status: "idle", errorMessage: undefined }))

    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
      const mockColors = ["#e53e3e", "#3182ce", "#d69e2e", "#1a1a1a", "#ffffff"]
      setColorPalette({
        detectedColors: mockColors,
        brandColors: ["#e53e3e", "#3182ce"],
        accuracy: 99,
      })
    }
    reader.readAsDataURL(file)
  }, [])

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

  const startProcessing = useCallback(async () => {
    if (!uploadedFile) return

    setProgress((prev) => ({ ...prev, status: "processing" }))
    setProcessingResult(null)
    setSvgPreview(null)

    let currentPhase = 1
    let currentProgress = 0
    const startTime = Date.now()

    const baseTime = Math.min(uploadedFile.size / (100 * 1024), 30)
    const complexityMultiplier = colorCount / 16
    const estimatedTime = baseTime * complexityMultiplier * 1000

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const progressRate = Math.random() * 2 + 0.5
      currentProgress += progressRate

      const currentPhaseData = PROCESSING_PHASES[currentPhase as keyof typeof PROCESSING_PHASES]

      if (currentProgress >= currentPhaseData.range[1]) {
        currentPhase++
        if (currentPhase > 5) {
          clearInterval(interval)

          const finalMetrics = {
            processingTime: Date.now() - startTime,
            pathCount: Math.floor(Math.random() * 500) + 200,
            colorCount: colorCount,
            sizeReduction: Math.floor(Math.random() * 30) + 50,
          }

          setProcessingResult({
            success: true,
            outputPath: `vectorized/${uploadedFile.name.replace(/\.[^/.]+$/, ".svg")}`,
            metrics: finalMetrics,
          })

          setSvgPreview(`<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <rect x="50" y="50" width="100" height="100" fill="#e53e3e"/>
            <circle cx="100" cy="100" r="30" fill="#3182ce"/>
            <polygon points="100,70 120,110 80,110" fill="#d69e2e"/>
          </svg>`)

          setProgress({
            phase: 5,
            percentage: 100,
            elapsedTime: Date.now() - startTime,
            estimatedTotal: Date.now() - startTime,
            currentOperation: "✓ COMPLETE",
            status: "complete",
          })
          return
        }
      }

      const phaseOperations = {
        1: "ANALYZING...",
        2: "QUANTIZING...",
        3: "DETECTING HOLES...",
        4: "GENERATING PATHS...",
        5: "OPTIMIZING...",
      }

      setProgress({
        phase: currentPhase as any,
        percentage: Math.min(currentProgress, 100),
        elapsedTime: elapsed,
        estimatedTotal: estimatedTime,
        currentOperation: phaseOperations[currentPhase as keyof typeof phaseOperations],
        status: "processing",
      })
    }, 150)
  }, [uploadedFile, colorCount])

  const generateCommand = useCallback(() => {
    if (!uploadedFile) return "python3 imagetracer.py input.png output.svg --preset color_perfect"

    const inputName = uploadedFile.name
    const outputName = inputName.replace(/\.[^/.]+$/, ".svg")

    return `python3 imagetracer.py ${inputName} ${outputName} --preset ${selectedPreset} --colors ${colorCount} --scale ${scaleMultiplier}`
  }, [uploadedFile, selectedPreset, colorCount, scaleMultiplier])

  const copyCommand = useCallback(() => {
    navigator.clipboard.writeText(generateCommand())
  }, [generateCommand])

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    return minutes > 0 ? `${minutes}M ${seconds % 60}S` : `${seconds}S`
  }

  const selectedPresetData = CORE_PRESETS.find((p) => p.id === selectedPreset) || CORE_PRESETS[0]

  return (
    <div className="min-h-screen bg-bauhaus-gray font-bauhaus relative">
      <BauhausDecoration />

      <div className="max-w-7xl mx-auto p-6 space-y-6 relative z-10">
        {/* Header */}
        <div className="bauhaus-card p-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bauhaus-logo-container">
                <Image src="/rv0-logo.png" alt="rv0" width={100} height={40} className="h-10 w-auto" priority />
              </div>
              <div>
                <h1 className="bauhaus-title text-2xl text-bauhaus-black">VECTOR STUDIO</h1>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-bauhaus-black text-white px-3 py-1">
                <BauhausShape type="circle" color="white" size="w-2 h-2" />
                <span className="text-xs font-bold">READY</span>
              </div>
            </div>
          </div>
          <BauhausShape type="square" color="red" size="w-4 h-4" className="absolute top-3 right-3" />
        </div>

        {/* Upload */}
        <div
          className="bauhaus-upload bauhaus-card p-8 text-center relative cursor-pointer"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          title="Drag & drop images here or click to browse. Supports PNG, JPG. Max 2MB."
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
            accept="image/png,image/jpeg,image/jpg"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFileUpload(file)
            }}
          />
        </div>

        {/* Error */}
        {progress.status === "error" && progress.errorMessage && (
          <div className="bauhaus-card bg-bauhaus-red text-white p-3">
            <span className="font-bold">{progress.errorMessage}</span>
          </div>
        )}

        {/* Progress */}
        {progress.status !== "idle" && progress.status !== "error" && (
          <div className="bauhaus-card p-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="bauhaus-title text-sm">PROGRESS</span>
                <span className="text-xs">
                  {progress.percentage.toFixed(0)}% | {formatTime(progress.elapsedTime)}
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
                      {PROCESSING_PHASES[progress.phase].name}
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
                  <div>
                    [{new Date().toLocaleTimeString()}] RV0: PROCESSING {uploadedFile?.name}
                  </div>
                  <div>
                    [{new Date().toLocaleTimeString()}] RV0: {colorPalette.detectedColors.length} COLORS DETECTED
                  </div>
                  <div className="text-bauhaus-yellow">
                    [{new Date().toLocaleTimeString()}] RV0: LAB CONVERSION COMPLETE
                  </div>
                  {progress.status === "complete" && (
                    <div className="text-bauhaus-yellow">
                      [{new Date().toLocaleTimeString()}] RV0: ✓ EXPORT COMPLETE
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Colors */}
        {colorPalette.detectedColors.length > 0 && (
          <div className="bauhaus-card p-4 relative">
            <h3 className="bauhaus-title text-sm mb-4">COLORS</h3>
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
        <div className="bauhaus-card p-4">
          <h3 className="bauhaus-title text-sm mb-4">PRESETS</h3>
          <div className="grid grid-cols-2 gap-4">
            {CORE_PRESETS.map((preset) => (
              <div
                key={preset.id}
                className={`p-4 border-3 cursor-pointer transition-all relative ${
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
                  <div className="absolute -top-2 -right-2 bg-bauhaus-red text-white px-2 py-1">
                    <span className="text-xs font-bold">★</span>
                  </div>
                )}

                <div className="flex items-center gap-3 mb-2">
                  <div
                    className={`w-6 h-6 bg-${preset.color} flex items-center justify-center text-white text-sm font-bold`}
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
        <div className="bauhaus-card p-4">
          <h3 className="bauhaus-title text-sm mb-4">PARAMETERS</h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label
                className="text-xs block mb-2"
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
              <label className="text-xs block mb-2" title="Output size multiplier for high-resolution exports">
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

        {/* Preview */}
        {uploadedFile && (
          <div className="bauhaus-card p-4">
            <h3 className="bauhaus-title text-sm mb-4">PREVIEW</h3>
            <div className="grid grid-cols-3 gap-4">
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
                  </div>
                ) : (
                  <div className="text-xs text-bauhaus-black opacity-70">PENDING</div>
                )}
              </div>
            </div>

            {progress.status === "idle" && uploadedFile && (
              <div className="mt-6 text-center">
                <button
                  onClick={startProcessing}
                  className="bauhaus-button bauhaus-button-red text-sm px-8 py-3"
                  title="Start vectorization with current settings"
                >
                  START VECTORIZATION
                </button>
              </div>
            )}
          </div>
        )}

        {/* Command */}
        <div className="bauhaus-card p-4">
          <h3 className="bauhaus-title text-sm mb-3">COMMAND</h3>
          <div className="bg-bauhaus-black text-white p-3 font-mono text-xs overflow-x-auto mb-3">
            <pre>{generateCommand()}</pre>
          </div>
          <div className="flex gap-3">
            <button className="bauhaus-button text-xs" onClick={copyCommand} title="Copy command to clipboard">
              COPY
            </button>
            <button
              className="bauhaus-button bauhaus-button-blue text-xs"
              disabled={!processingResult?.success}
              title="Download vectorized SVG file"
            >
              DOWNLOAD
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
