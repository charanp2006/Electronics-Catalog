import { useState } from 'react'
import { Plus, Pencil, Trash2, X } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import {
  createCategory,
  deleteCategory,
  listCategories,
  updateCategory,
  extractError,
} from '../api'
import { Input, TextArea, Loader, ErrorState, PageHeader } from '../ui'

const EMPTY = { name: '', slug: '', description: '', icon: '', image: '' }

export default function Categories() {
  const { data, loading, error, refetch } = useApi(listCategories, [])
  const [form, setForm] = useState(EMPTY)
  const [editingId, setEditingId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [formError, setFormError] = useState(null)

  const reset = () => {
    setForm(EMPTY)
    setEditingId(null)
    setFormError(null)
  }

  const edit = (category) => {
    setEditingId(category._id)
    setForm({
      name: category.name || '',
      slug: category.slug || '',
      description: category.description || '',
      icon: category.icon || '',
      image: category.image || '',
    })
  }

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setFormError(null)
    const payload = {
      name: form.name,
      slug: form.slug || null,
      description: form.description || null,
      icon: form.icon || null,
      image: form.image || null,
    }
    try {
      if (editingId) await updateCategory(editingId, payload)
      else await createCategory(payload)
      reset()
      refetch()
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setBusy(false)
    }
  }

  const remove = async (category) => {
    if (!window.confirm(`Delete "${category.name}"?`)) return
    setFormError(null)
    try {
      await deleteCategory(category._id)
      refetch()
    } catch (err) {
      setFormError(extractError(err))
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="categories" subtitle="catalog taxonomy" />

      {formError && (
        <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">{formError}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <form onSubmit={submit} className="panel frame space-y-4 p-4">
          <div className="flex items-center justify-between">
            <span className="label">{editingId ? 'edit category' : 'new category'}</span>
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
          <TextArea
            label="description"
            rows={2}
            value={form.description}
            onChange={(v) => setForm((f) => ({ ...f, description: v }))}
          />
          <Input label="icon" value={form.icon} onChange={(v) => setForm((f) => ({ ...f, icon: v }))} />
          <Input
            label="image url"
            value={form.image}
            onChange={(v) => setForm((f) => ({ ...f, image: v }))}
          />
          <button type="submit" disabled={busy} className="btn btn-primary w-full">
            <Plus size={14} /> {editingId ? 'save' : 'create'}
          </button>
        </form>

        <div className="lg:col-span-2">
          {loading && <Loader label="loading categories" />}
          {error && <ErrorState message={error} onRetry={refetch} />}
          {data && (
            <div className="panel frame divide-y divide-line/60">
              {data.map((category) => (
                <div key={category._id} className="flex items-center justify-between gap-3 p-3">
                  <div>
                    <p className="text-sm text-ink">{category.name}</p>
                    <p className="text-[0.65rem] text-dim">
                      /{category.slug} · {category.product_count} products
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <button type="button" onClick={() => edit(category)} className="btn px-2 py-1">
                      <Pencil size={13} />
                    </button>
                    <button
                      type="button"
                      onClick={() => remove(category)}
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
