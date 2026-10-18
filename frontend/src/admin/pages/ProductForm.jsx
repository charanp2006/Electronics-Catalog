import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { Plus, Trash2, ArrowLeft } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import {
  createProduct,
  getProductById,
  listBrands,
  listCategories,
  updateProduct,
  extractError,
} from '../api'
import { Input, TextArea, Select, Checkbox, Loader, PageHeader } from '../ui'

const EMPTY = {
  name: '',
  slug: '',
  brand: '',
  category: '',
  description: '',
  price: '',
  discount_price: '',
  stock: '0',
  image_urls: '',
  specifications: [],
  is_active: true,
  is_featured: false,
}

export default function ProductForm() {
  const { id } = useParams()
  const editing = Boolean(id)
  const navigate = useNavigate()

  const { data: brands } = useApi(listBrands, [])
  const { data: categories } = useApi(listCategories, [])

  const [form, setForm] = useState(EMPTY)
  const [loading, setLoading] = useState(editing)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!editing) return
    setLoading(true)
    getProductById(id)
      .then((p) =>
        setForm({
          name: p.name || '',
          slug: p.slug || '',
          brand: p.brand?.slug || '',
          category: p.category?.slug || '',
          description: p.description || '',
          price: p.price ?? '',
          discount_price: p.discount_price ?? '',
          stock: p.stock ?? 0,
          image_urls: (p.images || []).join(', '),
          specifications: p.specifications || [],
          is_active: p.is_active ?? true,
          is_featured: p.is_featured ?? false,
        })
      )
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [id, editing])

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const setSpec = (index, key, value) =>
    setForm((f) => {
      const specs = [...f.specifications]
      specs[index] = { ...specs[index], [key]: value }
      return { ...f, specifications: specs }
    })

  const addSpec = () =>
    setForm((f) => ({ ...f, specifications: [...f.specifications, { key: '', value: '' }] }))

  const removeSpec = (index) =>
    setForm((f) => ({ ...f, specifications: f.specifications.filter((_, i) => i !== index) }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    const payload = {
      name: form.name,
      slug: form.slug || null,
      brand: form.brand,
      category: form.category,
      description: form.description || null,
      price: Number(form.price),
      discount_price: form.discount_price === '' ? null : Number(form.discount_price),
      stock: Number(form.stock),
      image_urls: form.image_urls || null,
      specifications: form.specifications.filter((s) => s.key && s.value),
      is_active: form.is_active,
      is_featured: form.is_featured,
    }
    try {
      if (editing) await updateProduct(id, payload)
      else await createProduct(payload)
      navigate('/admin-cms/products')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <Loader label="loading unit" />

  const brandOptions = (brands || []).map((b) => ({ value: b.slug, label: b.name }))
  const categoryOptions = (categories || []).map((c) => ({ value: c.slug, label: c.name }))

  return (
    <div className="space-y-6">
      <PageHeader
        title={editing ? 'edit product' : 'new product'}
        subtitle={editing ? form.name : 'create catalog unit'}
        actions={
          <Link to="/admin-cms/products" className="btn">
            <ArrowLeft size={14} /> back
          </Link>
        }
      />

      {error && (
        <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">{error}</p>
      )}

      <form onSubmit={submit} className="grid gap-4 lg:grid-cols-3">
        <div className="panel frame space-y-4 p-4 lg:col-span-2">
          <Input label="name" required value={form.name} onChange={(v) => set('name', v)} />
          <Input
            label="slug (optional)"
            value={form.slug}
            onChange={(v) => set('slug', v)}
            placeholder="auto-generated from name"
          />
          <TextArea
            label="description"
            rows={4}
            value={form.description}
            onChange={(v) => set('description', v)}
          />

          <div>
            <div className="mb-2 flex items-center justify-between">
              <span className="label">specifications</span>
              <button type="button" onClick={addSpec} className="btn px-2 py-1">
                <Plus size={12} /> add
              </button>
            </div>
            <div className="space-y-2">
              {form.specifications.map((spec, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    value={spec.key}
                    placeholder="key"
                    onChange={(e) => setSpec(index, 'key', e.target.value)}
                    className="field w-1/3"
                  />
                  <input
                    value={spec.value}
                    placeholder="value"
                    onChange={(e) => setSpec(index, 'value', e.target.value)}
                    className="field grow"
                  />
                  <button
                    type="button"
                    onClick={() => removeSpec(index)}
                    className="btn btn-danger px-2"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}
              {form.specifications.length === 0 && (
                <p className="text-[0.65rem] text-dim">no specifications yet</p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="panel frame space-y-4 p-4">
            <Select
              label="brand"
              placeholder="select brand"
              value={form.brand}
              onChange={(v) => set('brand', v)}
              options={brandOptions}
            />
            <Select
              label="category"
              placeholder="select category"
              value={form.category}
              onChange={(v) => set('category', v)}
              options={categoryOptions}
            />
            <Input
              label="price (₹)"
              type="number"
              step="0.01"
              required
              value={form.price}
              onChange={(v) => set('price', v)}
            />
            <Input
              label="discount price (₹)"
              type="number"
              step="0.01"
              value={form.discount_price}
              onChange={(v) => set('discount_price', v)}
            />
            <Input
              label="stock"
              type="number"
              value={form.stock}
              onChange={(v) => set('stock', v)}
            />
          </div>

          <div className="panel frame space-y-3 p-4">
            <TextArea
              label="image urls (comma-separated)"
              rows={3}
              value={form.image_urls}
              onChange={(v) => set('image_urls', v)}
              placeholder="https://…, https://…"
            />
            <p className="text-[0.65rem] text-dim">First URL becomes the primary image.</p>
            <div className="flex gap-4">
              <Checkbox
                label="active"
                checked={form.is_active}
                onChange={(v) => set('is_active', v)}
              />
              <Checkbox
                label="featured"
                checked={form.is_featured}
                onChange={(v) => set('is_featured', v)}
              />
            </div>
          </div>

          <button type="submit" disabled={busy} className="btn btn-primary w-full">
            {busy ? 'saving…' : editing ? 'save changes' : 'create product'}
          </button>
        </div>
      </form>
    </div>
  )
}
