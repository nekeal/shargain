import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { NotificationFieldsPicker } from './NotificationFieldsPicker'
import type { AvailableFieldSchema } from '@/lib/api/types.gen'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}))

const makeField = (name: string, label: string, unit?: string): AvailableFieldSchema => ({
  name,
  label,
  type: 'string',
  unit,
  operators: [],
})

const TITLE = makeField('title', 'Title')
const PRICE = makeField('price', 'Price', 'zł')

const Wrapper = ({
  fields,
  initial = [],
}: {
  fields: Array<AvailableFieldSchema>
  initial?: Array<string>
}) => {
  const [selected, setSelected] = useState<Array<string>>(initial)
  return (
    <NotificationFieldsPicker
      availableFields={fields}
      selectedFields={selected}
      onChange={setSelected}
    />
  )
}

const openPicker = () => {
  fireEvent.click(screen.getByRole('button', { name: /urlSettings\.triggerPlaceholder/ }))
}

describe('NotificationFieldsPicker', () => {
  it('renders chips and count for the initial selection', () => {
    render(<Wrapper fields={[TITLE, PRICE]} initial={['title', 'price']} />)

    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Price')).toBeInTheDocument()
    expect(screen.getByText('2/2')).toBeInTheDocument()
  })

  it('removes a field when its chip X is clicked', () => {
    render(<Wrapper fields={[TITLE, PRICE]} initial={['title', 'price']} />)

    const removeButtons = screen.getAllByRole('button', { name: 'urlSettings.removeField' })
    fireEvent.click(removeButtons[0])

    expect(screen.queryByText('Title')).not.toBeInTheDocument()
    expect(screen.getByText('1/2')).toBeInTheDocument()
  })

  it('excludes stale selected ids not present in available fields', () => {
    render(<Wrapper fields={[TITLE]} initial={['title', 'ghost']} />)

    expect(screen.getByText('1/1')).toBeInTheDocument()
    expect(screen.queryByText('ghost')).not.toBeInTheDocument()
  })

  it('filters the list by search query', () => {
    const fields = [makeField('brand', 'Marka'), makeField('mileage', 'Przebieg'), makeField('price', 'Cena')]
    render(<Wrapper fields={fields} />)

    openPicker()
    const search = screen.getByPlaceholderText('urlSettings.searchPlaceholder')
    fireEvent.change(search, { target: { value: 'mark' } })

    expect(screen.getByText('Marka')).toBeInTheDocument()
    expect(screen.queryByText('Przebieg')).not.toBeInTheDocument()
    expect(screen.queryByText('Cena')).not.toBeInTheDocument()
  })

  it('shows a no-results message when nothing matches', () => {
    render(<Wrapper fields={[makeField('brand', 'Marka')]} />)

    openPicker()
    const search = screen.getByPlaceholderText('urlSettings.searchPlaceholder')
    fireEvent.change(search, { target: { value: 'zzz' } })

    expect(screen.getByText('urlSettings.noResults')).toBeInTheDocument()
    expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
  })

  it('selects all visible fields and clears them', () => {
    const fields = [makeField('brand', 'Marka'), makeField('mileage', 'Przebieg'), makeField('price', 'Cena')]
    render(<Wrapper fields={fields} />)

    openPicker()
    fireEvent.click(screen.getByRole('button', { name: 'urlSettings.selectAll' }))

    const boxes = screen.getAllByRole('checkbox')
    expect(boxes.every((box) => (box as HTMLInputElement).checked)).toBe(true)
    expect(screen.getByRole('button', { name: 'urlSettings.clear' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'urlSettings.clear' }))
    expect(screen.getAllByRole('checkbox').every((box) => !(box as HTMLInputElement).checked)).toBe(true)
  })

  it('renders the field unit in the list row', () => {
    render(<Wrapper fields={[makeField('mileage', 'Przebieg', 'km')]} />)

    openPicker()
    expect(screen.getByText('(km)')).toBeInTheDocument()
  })

  it('stays usable with 30 fields in a scrollable list', () => {
    const fields = Array.from({ length: 30 }, (_, i) => makeField(`field_${i}`, `Pole ${i}`))
    render(<Wrapper fields={fields} />)

    openPicker()
    expect(screen.getAllByRole('checkbox')).toHaveLength(30)
    expect(screen.getByRole('listbox').className).toContain('overflow-y-auto')
    expect(screen.getByRole('listbox').className).toContain('max-h-[min(280px')

    const boxes = screen.getAllByRole('checkbox')
    fireEvent.click(boxes[0])
    expect((boxes[0] as HTMLInputElement).checked).toBe(true)
  })
})
