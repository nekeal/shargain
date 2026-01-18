import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// not sure if this file is needed
// Cleanup after each test
afterEach(() => {
  cleanup()
})
