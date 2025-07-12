"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Upload, Copy, Download, Share, Settings, ChevronDown, ChevronUp, Play, Pause, Square } from "lucide-react"

interface ProgressState {
  phase: 1 | 2 | 3 | 4 | 5 | 6
  percentage: number
  elapsedTime: number
  estimatedTotal: number
  currentOperation: string
  status: "idle" | "processing" | "complete" | "error" | "paused"
}

interface ColorPalette {
  detectedColors: string[]
  brandColors: string[]
  accuracy: number
}

interface AdvancedParams {
  colors: number
  colorSampling: "palette" | "random" | "deterministic"
  colorCycles: number
  lineThreshold: number
  curveThreshold: number
  pathOmit: number
  rightAngleEnhance: boolean
  resolution: number | "auto"
  blur: number
  scale: number
  strokeWidth: number
  viewBox: boolean
  description: boolean
}

const PHASES = {
  1: { name: "Image Loading & Analysis", range: [0, 10] },
  2: { name: "Color Quantization", range: [10, 25] },
  3: { name: "Edge Detection", range: [25, 45] },
  4: { name: "Path Tracing", range: [45, 75] },
  5: { name: "SVG Generation", range: [75, 90] },
  6: { name: "Optimization & Export", range: [90, 100] },
}

const PRESETS = [
  { id: "default", name: "Default", desc: "Balanced quality/performance", icon: "⚖️" },
  { id: "sharp", name: "Sharp", desc: "Logo-perfect high-fidelity", icon: "🎯" },
  { id: "posterized1", name: "Posterized 1", desc: "2-color fast posterization", icon: "🎨" },
  { id: "posterized2", name: "Posterized 2", desc: "4-color blur posterization", icon: "🎭" },
  { id: "posterized3", name: "Posterized 3", desc: "3-color custom posterization", icon: "🖼️" },
  { id: "curvy", name: "Curvy", desc: "Smooth curves for organic shapes", icon: "🌊" },
  { id: "detailed", name: "Detailed", desc: "Maximum detail (slow)", icon: "🔍" },
  { id: "smoothed", name: "Smoothed", desc: "Blur preprocessing", icon: "✨" },
  { id: "grayscale", name: "Grayscale", desc: "Monochrome 7 gray levels", icon: "⚫" },
  { id: "fixedpalette", name: "Fixed Palette", desc: "27-color consistent", icon: "🎨" },
  { id: "randomsampling1", name: "Random Sampling 1", desc: "Alternative sampling (8)", icon: "🎲" },
  { id: "randomsampling2", name: "Random Sampling 2", desc: "Alternative sampling (64)", icon: "🎰" },
  { id: "artistic1", name: "Artistic 1", desc: "Stylized with stroke outline", icon: "🎨" },
  { id: "artistic2", name: "Artistic 2", desc: "High-contrast artistic", icon: "🎭" },
  { id: "artistic3", name: "Artistic 3", desc: "Simplified artistic style", icon: "🖌️" },
  { id: "artistic4", name: "Artistic 4", desc: "Complex with blur effects", icon: "🌈" },
]

const PERFORMANCE_LEVELS = {
  0: { time: 5, size: "Small", quality: 70, desc: "Draft" },
  1: { time: 15, size: "Medium", quality: 85, desc: "Standard" },
  2: { time: 45, size: "Large", quality: 95, desc: "High" },
  3: { time: 120, size: "Very Large", quality: 100, desc: "Maximum" },
}

export default function VectorOptimizationStudio() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [progress, setProgress] = useState<ProgressState>({
    phase: 1,
    percentage: 0,
    elapsedTime: 0,
    estimatedTotal: 0,
    currentOperation: "Ready to process",
    status: "idle",
  })
  const [colorPalette, setColorPalette] = useState<ColorPalette>({
    detectedColors: ["#f7931e", "#000000", "#ffffff", "#cccccc"],
    brandColors: ["#f7931e", "#000000", "#ffffff"],
    accuracy: 100,
  })
  const [selectedPreset, setSelectedPreset] = useState<string>("default")
  const [performanceLevel, setPerformanceLevel] = useState<number>(1)
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false)
  const [showLogs, setShowLogs] = useState<boolean>(false)
  const [advancedParams, setAdvancedParams] = useState<AdvancedParams>({
    colors: 16,
    colorSampling: "palette",
    colorCycles: 3,
    lineThreshold: 1.0,
    curveThreshold: 1.0,
    pathOmit: 8,
    rightAngleEnhance: true,
    resolution: "auto",
    blur: 0,
    scale: 1.0,
    strokeWidth: 1,
    viewBox: true,
    description: false,
  })

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = useCallback((file: File) => {
    setUploadedFile(file)
    // Simulate color detection
    const mockColors = ["#f7931e", "#000000", "#ffffff", "#cccccc", "#666666"]
    setColorPalette((prev) => ({
      ...prev,
      detectedColors: mockColors,
    }))
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0 && files[0].type.startsWith("image/")) {
        handleFileUpload(files[0])
      }
    },
    [handleFileUpload],
  )

  const startProcessing = useCallback(() => {
    setProgress((prev) => ({ ...prev, status: "processing" }))

    // Simulate processing phases
    let currentPhase = 1
    let currentProgress = 0
    const startTime = Date.now()

    const interval = setInterval(() => {
      currentProgress += Math.random() * 3

      if (currentProgress >= PHASES[currentPhase as keyof typeof PHASES].range[1]) {
        currentPhase++
        if (currentPhase > 6) {
          clearInterval(interval)
          setProgress({
            phase: 6,
            percentage: 100,
            elapsedTime: Date.now() - startTime,
            estimatedTotal: Date.now() - startTime,
            currentOperation: "Processing complete",
            status: "complete",
          })
          return
        }
      }

      setProgress({
        phase: currentPhase as any,
        percentage: Math.min(currentProgress, 100),
        elapsedTime: Date.now() - startTime,
        estimatedTotal: (Date.now() - startTime) * (100 / currentProgress),
        currentOperation: `${PHASES[currentPhase as keyof typeof PHASES].name} - Processing...`,
        status: "processing",
      })
    }, 200)
  }, [])

  const generateCommand = useCallback(() => {
    const parts = ["python vectorize.py"]

    if (uploadedFile) {
      parts.push(uploadedFile.name)
    } else {
      parts.push("image.png")
    }

    if (selectedPreset !== "default") {
      parts.push(`--preset ${selectedPreset}`)
    }

    if (colorPalette.brandColors.length > 0) {
      parts.push(`--brand-palette "${colorPalette.brandColors.join(",")}"`)
    }

    const perfLevel = PERFORMANCE_LEVELS[performanceLevel as keyof typeof PERFORMANCE_LEVELS]
    if (performanceLevel !== 1) {
      parts.push(`--performance ${perfLevel.desc.toLowerCase()}`)
    }

    if (advancedParams.resolution !== "auto") {
      parts.push(`--resolution ${advancedParams.resolution}`)
    }

    parts.push("--overwrite")

    return parts.join(" \\\n  ")
  }, [uploadedFile, selectedPreset, colorPalette.brandColors, performanceLevel, advancedParams])

  const copyCommand = useCallback(() => {
    navigator.clipboard.writeText(generateCommand())
  }, [generateCommand])

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`
  }

  const getProgressColor = (elapsedTime: number) => {
    if (elapsedTime < 30000) return "#22c55e"
    if (elapsedTime < 120000) return "#eab308"
    if (elapsedTime < 300000) return "#f97316"
    return "#ef4444"
  }

  return (
    <div className="min-h-screen bg-white font-mono">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 pb-4">
          <h1 className="text-2xl font-bold text-black">● Vector Optimization Studio</h1>
          <Button variant="outline" size="sm">
            Help
          </Button>
        </div>

        {/* Upload Zone */}
        <Card className="border-2 border-dashed border-gray-300">
          <CardContent className="p-8">
            <div
              className="text-center space-y-4 cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div>
                <h3 className="text-lg font-semibold">Drag & drop images/PDFs here or click to browse</h3>
                <p className="text-sm text-gray-600">Supports: PNG, JPG, PDF • Max size: 50MB</p>
              </div>
              {uploadedFile && (
                <div className="text-sm text-green-600">
                  ✓ {uploadedFile.name} ({Math.round(uploadedFile.size / 1024)}KB)
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileUpload(file)
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Progress Tracking */}
        {progress.status !== "idle" && (
          <Card className="border border-gray-300">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold">Vectorization Progress</span>
                  <span className="text-sm">
                    {progress.percentage.toFixed(0)}% | {formatTime(progress.elapsedTime)}
                  </span>
                </div>

                <div className="relative">
                  <Progress
                    value={progress.percentage}
                    className="h-3"
                    style={
                      {
                        "--progress-background": getProgressColor(progress.elapsedTime),
                      } as React.CSSProperties
                    }
                  />
                  <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
                    Phase {progress.phase}: {PHASES[progress.phase].name} - {progress.currentOperation}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={() => setShowLogs(!showLogs)}>
                    {showLogs ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    Show Detailed Log
                  </Button>

                  {progress.status === "processing" && (
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Pause className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Square className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>

                {showLogs && (
                  <div className="bg-gray-50 p-4 rounded border text-xs font-mono space-y-1 max-h-40 overflow-y-auto">
                    <div>[15:23:45] Phase 1: Image loaded: {uploadedFile?.name || "image.png"} (864×764, 308KB)</div>
                    <div>[15:23:47] Phase 2: Color detection: 8 dominant colors found</div>
                    <div className="text-green-600">[15:23:47] Phase 2: Brand palette applied: 3 exact colors</div>
                    <div>[15:23:49] Phase 2: K-means quantization: 50,000 samples processed</div>
                    <div>[15:23:52] Phase 3: Edge detection: 15,847 edge nodes identified</div>
                    <div>[15:23:55] Phase 4: Layer 1 processing: 423 orange paths traced</div>
                    <div>[15:23:58] Phase 4: Layer 2 processing: 289 black paths traced</div>
                    <div>[15:24:01] Phase 4: Layer 3 processing: 180 white paths traced</div>
                    <div>[15:24:03] Phase 5: SVG optimization: 892 final paths</div>
                    {progress.status === "complete" && (
                      <div className="text-green-600">
                        [15:24:04] Phase 6: ✅ Export complete: vectorized/output.svg
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Color Analysis & Brand Palette */}
        <Card className="border border-gray-300">
          <CardHeader>
            <CardTitle className="text-lg">Color Analysis & Brand Palette</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm font-medium">Auto-detected Colors:</Label>
              <div className="flex gap-2 mt-2">
                {colorPalette.detectedColors.map((color, i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded border border-gray-300 cursor-pointer"
                    style={{ backgroundColor: color }}
                    title={color}
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
              <Label className="text-sm font-medium">Brand Color Palette:</Label>
              <div className="flex gap-2 mt-2 items-center">
                {colorPalette.brandColors.map((color, i) => (
                  <div key={i} className="relative">
                    <Input
                      type="color"
                      value={color}
                      onChange={(e) => {
                        const newColors = [...colorPalette.brandColors]
                        newColors[i] = e.target.value
                        setColorPalette((prev) => ({ ...prev, brandColors: newColors }))
                      }}
                      className="w-8 h-8 p-0 border border-gray-300 rounded cursor-pointer"
                    />
                  </div>
                ))}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setColorPalette((prev) => ({
                      ...prev,
                      brandColors: [...prev.brandColors, "#000000"],
                    }))
                  }}
                >
                  + Add Color
                </Button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className={`text-sm ${colorPalette.accuracy === 100 ? "text-green-600" : "text-orange-600"}`}>
                {colorPalette.accuracy === 100 ? "✅" : "⚠️"} {colorPalette.accuracy}% brand color preservation
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Preset Selection */}
        <Card className="border border-gray-300">
          <CardHeader>
            <CardTitle className="text-lg">Preset Selection</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              {PRESETS.map((preset) => (
                <div
                  key={preset.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedPreset === preset.id ? "border-black bg-gray-50" : "border-gray-300 hover:border-gray-400"
                  }`}
                  onClick={() => setSelectedPreset(preset.id)}
                >
                  <div className="text-2xl mb-2">{preset.icon}</div>
                  <h4 className="font-semibold text-sm">{preset.name}</h4>
                  <p className="text-xs text-gray-600 mt-1">{preset.desc}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Performance Tuning */}
        <Card className="border border-gray-300">
          <CardHeader>
            <CardTitle className="text-lg">Performance Tuning</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm font-medium">Speed vs Quality Balance:</Label>
              <div className="mt-2">
                <Slider
                  value={[performanceLevel]}
                  onValueChange={(value) => setPerformanceLevel(value[0])}
                  max={3}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Fast</span>
                  <span>Balanced</span>
                  <span>Quality</span>
                </div>
              </div>
            </div>

            <div className="flex gap-6 text-sm">
              <span>Time: ~{PERFORMANCE_LEVELS[performanceLevel as keyof typeof PERFORMANCE_LEVELS].time}s</span>
              <span>Size: {PERFORMANCE_LEVELS[performanceLevel as keyof typeof PERFORMANCE_LEVELS].size}</span>
              <span>Quality: {PERFORMANCE_LEVELS[performanceLevel as keyof typeof PERFORMANCE_LEVELS].quality}%</span>
            </div>
          </CardContent>
        </Card>

        {/* Advanced Parameters */}
        <Card className="border border-gray-300">
          <CardHeader>
            <CardTitle
              className="text-lg cursor-pointer flex items-center gap-2"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              Advanced Parameters
            </CardTitle>
          </CardHeader>
          {showAdvanced && (
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold">Color Settings</h4>
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="colors" className="text-sm">
                        Colors (1-256):
                      </Label>
                      <Input
                        id="colors"
                        type="number"
                        min="1"
                        max="256"
                        value={advancedParams.colors}
                        onChange={(e) =>
                          setAdvancedParams((prev) => ({ ...prev, colors: Number.parseInt(e.target.value) }))
                        }
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="sampling" className="text-sm">
                        Sampling:
                      </Label>
                      <Select
                        value={advancedParams.colorSampling}
                        onValueChange={(value: any) => setAdvancedParams((prev) => ({ ...prev, colorSampling: value }))}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="palette">Palette</SelectItem>
                          <SelectItem value="random">Random</SelectItem>
                          <SelectItem value="deterministic">Deterministic</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="cycles" className="text-sm">
                        Cycles (1-10):
                      </Label>
                      <Input
                        id="cycles"
                        type="number"
                        min="1"
                        max="10"
                        value={advancedParams.colorCycles}
                        onChange={(e) =>
                          setAdvancedParams((prev) => ({ ...prev, colorCycles: Number.parseInt(e.target.value) }))
                        }
                        className="mt-1"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold">Quality Settings</h4>
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="lineThreshold" className="text-sm">
                        Line Threshold:
                      </Label>
                      <Slider
                        value={[advancedParams.lineThreshold]}
                        onValueChange={(value) => setAdvancedParams((prev) => ({ ...prev, lineThreshold: value[0] }))}
                        min={0.01}
                        max={10}
                        step={0.01}
                        className="mt-2"
                      />
                      <span className="text-xs text-gray-600">{advancedParams.lineThreshold.toFixed(2)}</span>
                    </div>
                    <div>
                      <Label htmlFor="curveThreshold" className="text-sm">
                        Curve Threshold:
                      </Label>
                      <Slider
                        value={[advancedParams.curveThreshold]}
                        onValueChange={(value) => setAdvancedParams((prev) => ({ ...prev, curveThreshold: value[0] }))}
                        min={0.01}
                        max={10}
                        step={0.01}
                        className="mt-2"
                      />
                      <span className="text-xs text-gray-600">{advancedParams.curveThreshold.toFixed(2)}</span>
                    </div>
                    <div>
                      <Label htmlFor="pathOmit" className="text-sm">
                        Path Omit:
                      </Label>
                      <Slider
                        value={[advancedParams.pathOmit]}
                        onValueChange={(value) => setAdvancedParams((prev) => ({ ...prev, pathOmit: value[0] }))}
                        min={0}
                        max={50}
                        className="mt-2"
                      />
                      <span className="text-xs text-gray-600">{advancedParams.pathOmit}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="rightAngle"
                        checked={advancedParams.rightAngleEnhance}
                        onCheckedChange={(checked) =>
                          setAdvancedParams((prev) => ({ ...prev, rightAngleEnhance: !!checked }))
                        }
                      />
                      <Label htmlFor="rightAngle" className="text-sm">
                        Right Angle Enhancement
                      </Label>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Preview & Results */}
        {uploadedFile && (
          <Card className="border border-gray-300">
            <CardHeader>
              <CardTitle className="text-lg">Preview & Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center">
                  <h4 className="font-semibold mb-2">Original</h4>
                  <div className="aspect-square bg-gray-100 border border-gray-300 rounded flex items-center justify-center">
                    <span className="text-gray-500">Image Preview</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-2">
                    <div>864×764 PNG</div>
                    <div>1.2MB</div>
                  </div>
                </div>

                <div className="text-center">
                  <h4 className="font-semibold mb-2">Vectorized</h4>
                  <div className="aspect-square bg-gray-100 border border-gray-300 rounded flex items-center justify-center">
                    <span className="text-gray-500">SVG Preview</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-2">
                    <div>892 paths</div>
                    <div>3 colors</div>
                  </div>
                </div>

                <div className="text-center">
                  <h4 className="font-semibold mb-2">Performance Metrics</h4>
                  <div className="text-left space-y-1 text-sm">
                    <div>Time: 21.4s</div>
                    <div>Paths: 1,247→892</div>
                    <div>Accuracy: 100%</div>
                    <div>Size reduction: 67%</div>
                  </div>
                </div>
              </div>

              {progress.status === "idle" && (
                <div className="mt-6 text-center">
                  <Button onClick={startProcessing} className="bg-black text-white hover:bg-gray-800">
                    <Play className="h-4 w-4 mr-2" />
                    Start Vectorization
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Generated Command & Export */}
        <Card className="border border-gray-300">
          <CardHeader>
            <CardTitle className="text-lg">Generated Command & Export</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gray-50 p-4 rounded border font-mono text-sm overflow-x-auto">
              <pre>{generateCommand()}</pre>
            </div>

            <div className="flex gap-2 flex-wrap">
              <Button variant="outline" size="sm" onClick={copyCommand}>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button variant="outline" size="sm">
                <Share className="h-4 w-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Save Preset
              </Button>
            </div>

            <div>
              <Label htmlFor="exportFormat" className="text-sm">
                Export Format:
              </Label>
              <Select defaultValue="bash">
                <SelectTrigger className="mt-1 w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bash">Bash Script (.sh)</SelectItem>
                  <SelectItem value="batch">Batch File (.bat)</SelectItem>
                  <SelectItem value="json">Settings JSON</SelectItem>
                  <SelectItem value="url">Shareable URL</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
