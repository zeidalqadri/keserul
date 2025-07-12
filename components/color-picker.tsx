"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

interface ColorPickerProps {
  value: string
  onChange: (color: string) => void
  onRemove?: () => void
}

export function ColorPicker({ value, onChange, onRemove }: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="flex items-center gap-2">
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="w-8 h-8 p-0 border-2 bg-transparent" style={{ backgroundColor: value }}>
            <span className="sr-only">Pick color</span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-64">
          <div className="space-y-3">
            <Input type="color" value={value} onChange={(e) => onChange(e.target.value)} className="w-full h-32" />
            <Input
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder="#000000"
              className="font-mono"
            />
          </div>
        </PopoverContent>
      </Popover>

      {onRemove && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRemove}
          className="text-red-600 hover:text-red-700 bg-transparent"
        >
          ×
        </Button>
      )}
    </div>
  )
}
