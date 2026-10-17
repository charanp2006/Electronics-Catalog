import { motion } from 'motion/react'

export default function GridBackdrop({ className = '' }) {
  return (
    <div
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden="true"
    >
      <div className="grid-bg absolute -inset-10 opacity-30" />

      <motion.div
        className="grid-glow absolute -inset-10"
        animate={{ opacity: [0.06, 0.3, 0.06] }}
        transition={{ duration: 5.5, ease: 'easeInOut', repeat: Infinity }}
      />

      <motion.div
        className="grid-glow grid-glow-spot absolute -inset-10"
        style={{ '--gx': '-30%', '--gy': '0%' }}
        animate={{ '--gx': ['-30%', '130%'], '--gy': ['0%', '90%'] }}
        transition={{ duration: 8, ease: 'easeInOut', repeat: Infinity, repeatDelay: 0.4 }}
      />
    </div>
  )
}
