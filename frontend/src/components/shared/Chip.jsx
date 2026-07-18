const VARIANTS = {
  neutral: 'bg-surface-container-low text-on-surface-variant border-outline-variant',
  success: 'bg-secondary-container text-on-secondary-container border-secondary',
  warning: 'bg-tertiary-fixed text-on-tertiary-fixed-variant border-tertiary',
  danger: 'bg-error-container text-on-error-container border-error',
}

export default function Chip({ children, variant = 'neutral', className = '' }) {
  return (
    <span
      className={`
        inline-flex items-center gap-xs px-md py-xs rounded-full border
        font-label-sm text-label-sm uppercase tracking-wider
        ${VARIANTS[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  )
}