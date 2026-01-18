import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/legal/terms')({
  component: TermsComponent,
})

function TermsComponent() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">Terms of Service</h1>
        <p className="text-gray-600">The official Terms of Service are currently under legal review. This page is a placeholder.</p>
      </div>
    </div>
  )
}
