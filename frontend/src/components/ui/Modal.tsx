"use client";

import type { ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";

type ModalProps = {
  open: boolean;
  title?: string;
  onClose: () => void;
  dismissible?: boolean;
  children: ReactNode;
};

export function Modal({
  open,
  title,
  onClose,
  dismissible = true,
  children,
}: ModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="dialog"
          aria-modal="true"
        >
          {dismissible ? (
            <button
              className="absolute inset-0 cursor-default bg-black/30 backdrop-blur-sm"
              onClick={onClose}
              aria-label="Cerrar modal"
              type="button"
            />
          ) : (
            <div
              className="absolute inset-0 bg-black/30 backdrop-blur-sm"
              aria-hidden="true"
            />
          )}
          <motion.div
            className="relative z-10 w-full max-w-xl rounded-3xl border border-white/60 bg-white/90 p-6 shadow-[0_30px_80px_rgba(15,30,30,0.25)] backdrop-blur-xl"
            initial={{ scale: 0.96, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.96, y: 20, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-start justify-between gap-4">
              {title && (
                <h3 className="text-lg font-semibold text-[var(--foreground)]">
                  {title}
                </h3>
              )}
              {dismissible && (
                <button
                  onClick={onClose}
                  className="rounded-full border border-black/10 px-3 py-1 text-xs font-semibold text-[var(--foreground)] hover:bg-black/5"
                  type="button"
                >
                  Cerrar
                </button>
              )}
            </div>
            <div className="mt-4 text-sm text-[var(--muted)]">{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
