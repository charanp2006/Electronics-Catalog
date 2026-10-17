export default function Field({ label, type = 'text', value, onChange, placeholder }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <span className="flex items-center border border-line-2 bg-bg transition focus-within:border-phos">
        <span className="select-none pl-2.5 pr-1 text-phos">{'>'}</span>
        <input
          type={type}
          required
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-transparent py-2 pr-2.5 text-xs text-ink outline-none placeholder:text-[#5c6c75]"
        />
      </span>
    </label>
  )
}
