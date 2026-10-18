import { useState } from 'react'
import { Plus, Pencil, Trash2, X } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { createBrand, deleteBrand, listBrands, updateBrand, extractError } from '../api'
import { Input, Loader, ErrorState, PageHeader } from '../ui'

const EMPTY = { name: '', slug: '', country: '', logo: '' }

export default function Brands() {
  const { data, loading, error, refetch } = useApi(listBrands, [])
  const [form, setForm] = useState(EMPTY)
  const [editingId, setEditingId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [formError, setFormError] = useState(null)

  const reset = () => {
    setForm(EMPTY)
    setEditingId(null)
    setFormError(null)
  }

  const edit = (brand) => {
    setEditingId(brand._id)
    setForm({
      name: brand.name || '',
      slug: brand.slug || '',
      country: brand.country || '',
      logo: brand.logo || '',
    })
  }

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setFormError(null)
    const payload = {
      name: form.name,
      slug: form.slug || null,
      country: form.country || null,
      logo: form.logo || null,
    }
    try {
      if (editingId) await updateBrand(editingId, payload)
      else await createBrand(payload)
      reset()
      refetch()
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setBusy(false)
    }
  }

  const remove = async (brand) => {
    if (!window.confirm(`Delete "${brand.name}"?`)) return
    setFormError(null)
    try {
      await deleteBrand(brand._id)
      refetch()
    } catch (err) {
      setFormError(extractError(err))
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="brands" subtitle="manufacturers" />

      {formError && (
        <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">{formError}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <form onSubmit={submit} className="panel frame space-y-4 p-4">
          <div className="flex items-center justify-between">
            <span className="label">{editingId ? 'edit brand' : 'new brand'}</span>
            {editingId && (
              <button type="button" onClick={reset} className="btn px-2 py-1">
                <X size={13} />
              </button>
            )}
          </div>
          <Input label="name" required value={form.name} onChange={(v) => setForm((f) => ({ ...f, name: v }))} />
          <Input
            label="slug (optional)"
            value={form.slug}
            onChange={(v) => setForm((f) => ({ ...f, slug: v }))}
          />
          <Input
            label="country"
            value={form.country}
            onChange={(v) => setForm((f) => ({ ...f, country: v }))}
          />
          <Input label="logo url" value={form.logo} onChange={(v) => setForm((f) => ({ ...f, logo: v }))} />
          <button type="submit" disabled={busy} className="btn btn-primary w-full">
            <Plus size={14} /> {editingId ? 'save' : 'create'}
          </button>
        </form>

        <div className="lg:col-span-2">
          {loading && <Loader label="loading brands" />}
          {error && <ErrorState message={error} onRetry={refetch} />}
          {data && (
            <div className="panel frame divide-y divide-line/60">
              {data.map((brand) => (
                <div key={brand._id} className="flex items-center justify-between gap-3 p-3">
                  <div className="flex items-center gap-3">
                    {brand.logo && (
                      <img src={brand.logo} alt="" className="h-8 w-14 border border-line object-cover" />
                    )}
                    <div>
                      <p className="text-sm text-ink">{brand.name}</p>
                      <p className="text-[0.65rem] text-dim">
                        /{brand.slug}
                        {brand.country ? ` · ${brand.country}` : ''} · {brand.product_count} products
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button type="button" onClick={() => edit(brand)} className="btn px-2 py-1">
                      <Pencil size={13} />
                    </button>
                    <button
                      type="button"
                      onClick={() => remove(brand)}
                      className="btn btn-danger px-2 py-1"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
