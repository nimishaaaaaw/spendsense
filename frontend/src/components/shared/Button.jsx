const VARIANTS = {
  primary: 'bg-primary text-on-primary hover:bg-primary-container',
  secondary: 'bg-surface-container-low text-on-surface border border-outline-variant hover:bg-surface-container',
  danger: 'bg-error text-on-error hover:opacity-90',
  ghost: 'bg-transparent text-primary hover:bg-primary/5',
}

export default function Button({ children, variant = 'primary', className = '', onClick, disabled = false, type = 'button' }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        px-md py-sm rounded-xl font-label-md text-label-md
        transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
        ${VARIANTS[variant]}
        ${className}
      `}
    >
      {children}
    </button>
  )
}