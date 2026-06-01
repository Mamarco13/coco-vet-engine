"use client";

import { useRef, useState } from "react";
import { cn } from "@/lib/utils";

type UploadZoneProps = {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
  accept?: string;
  maxFiles?: number;
  helperText?: string;
};

export function UploadZone({
  onFiles,
  disabled,
  accept = "image/*",
  maxFiles = 6,
  helperText = "Arrastra imagenes aqui o haz click para buscarlas",
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const files = Array.from(fileList).slice(0, maxFiles);
    onFiles(files);
  };

  return (
    <div
      className={cn(
        "flex min-h-[180px] flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-black/10 bg-white/70 px-6 py-8 text-center transition",
        isDragging && "border-[var(--accent)] bg-[var(--accent-2)]",
        disabled && "opacity-60 pointer-events-none"
      )}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-black/5 text-xl">
        +
      </div>
      <div className="text-sm font-semibold text-[var(--foreground)]">{helperText}</div>
      <p className="text-xs text-[var(--muted)]">Maximo {maxFiles} archivos JPG o PNG.</p>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="mt-2 rounded-full border border-black/10 px-4 py-2 text-xs font-semibold text-[var(--foreground)] hover:bg-black/5"
      >
        Elegir archivos
      </button>
    </div>
  );
}
