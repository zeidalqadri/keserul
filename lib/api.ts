// API service for rv0 backend integration
export interface ApiConfig {
  backend: string
  bridge: string
}

export interface ProcessingOptions {
  preset: string
  colors: number
  scale: number
  brandColors?: string[]
}

export interface ProcessingStatus {
  id: string
  status: "queued" | "processing" | "complete" | "error"
  phase: number
  percentage: number
  currentOperation: string
  elapsedTime: number
  estimatedTotal?: number
  error?: string
}

export interface ProcessingResult {
  id: string
  success: boolean
  outputUrl?: string
  svgContent?: string
  metrics?: {
    processingTime: number
    pathCount: number
    colorCount: number
    sizeReduction: number
    originalSize: number
    outputSize: number
  }
  error?: string
}

const API_CONFIG: ApiConfig = {
  backend: "https://rastervector-n6ofijmqgq-uc.a.run.app",
  bridge: "https://rastervector-api.zeidalqadri.workers.dev",
}

class RV0ApiService {
  private config: ApiConfig

  constructor(config: ApiConfig) {
    this.config = config
  }

  async checkBackendStatus(): Promise<{ status: "online" | "offline"; version?: string }> {
    try {
      const response = await fetch(`${this.config.bridge}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })

      if (response.ok) {
        const data = await response.json()
        return { status: "online", version: data.version }
      }
      return { status: "offline" }
    } catch (error) {
      console.error("Backend health check failed:", error)
      return { status: "offline" }
    }
  }

  async uploadAndProcess(file: File, options: ProcessingOptions): Promise<{ jobId: string }> {
    const formData = new FormData()
    formData.append("image", file)
    formData.append("preset", options.preset)
    formData.append("colors", options.colors.toString())
    formData.append("scale", options.scale.toString())

    if (options.brandColors && options.brandColors.length > 0) {
      formData.append("brandColors", JSON.stringify(options.brandColors))
    }

    const response = await fetch(`${this.config.bridge}/process`, {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Upload failed" }))
      throw new Error(error.error || `HTTP ${response.status}`)
    }

    const result = await response.json()
    return { jobId: result.jobId }
  }

  async getProcessingStatus(jobId: string): Promise<ProcessingStatus> {
    const response = await fetch(`${this.config.bridge}/status/${jobId}`)

    if (!response.ok) {
      throw new Error(`Status check failed: HTTP ${response.status}`)
    }

    return await response.json()
  }

  async getResult(jobId: string): Promise<ProcessingResult> {
    const response = await fetch(`${this.config.bridge}/result/${jobId}`)

    if (!response.ok) {
      throw new Error(`Result fetch failed: HTTP ${response.status}`)
    }

    return await response.json()
  }

  async downloadSvg(jobId: string): Promise<Blob> {
    const response = await fetch(`${this.config.bridge}/download/${jobId}`)

    if (!response.ok) {
      throw new Error(`Download failed: HTTP ${response.status}`)
    }

    return await response.blob()
  }

  async analyzeColors(file: File): Promise<{ colors: string[]; accuracy: number }> {
    const formData = new FormData()
    formData.append("image", file)

    const response = await fetch(`${this.config.bridge}/analyze-colors`, {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Color analysis failed: HTTP ${response.status}`)
    }

    return await response.json()
  }

  getApiDocumentation(): string {
    return this.config.bridge
  }

  generateCurlCommand(file: File, options: ProcessingOptions): string {
    const brandColorsParam =
      options.brandColors && options.brandColors.length > 0
        ? ` -F "brandColors=${JSON.stringify(options.brandColors)}"`
        : ""

    return `curl -X POST "${this.config.bridge}/process" \\
  -F "image=@${file.name}" \\
  -F "preset=${options.preset}" \\
  -F "colors=${options.colors}" \\
  -F "scale=${options.scale}"${brandColorsParam}`
  }
}

export const rv0Api = new RV0ApiService(API_CONFIG)
