// eslint.config.js
import js from '@eslint/js'
import { tanstackConfig } from '@tanstack/eslint-config'
import pluginRouter from '@tanstack/eslint-plugin-router'
import pluginReact from 'eslint-plugin-react'
import pluginReactHooks from 'eslint-plugin-react-hooks'

export default [
    // 1) Generic JS/TS rules from TanStack
    ...tanstackConfig,
    {
        rules: {
            'pnpm/json-enforce-catalog': 'off'     // <-- disables only this rule
        }
    },

    // 2) Router plugin – all recommended rules
    ...pluginRouter.configs['flat/recommended'],

    // 3) React rules (customised flat config)
    {
        files: ['**/*.{js,jsx,ts,tsx}'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            parserOptions: {
                ecmaFeatures: { jsx: true }
            }
        },
        plugins: {
            react: pluginReact,
            'react-hooks': pluginReactHooks
        },
        rules: {
            ...pluginReact.configs.recommended.rules,
            ...pluginReactHooks.configs.recommended.rules,
            'react/react-in-jsx-scope': 'off'  // Vite/Next.js don’t need React in scope
        },
        settings: {
            react: { version: 'detect' }
        }
    },

    // 4) Global ignores (optional)
    {
        ignores: ['dist', 'node_modules', '*.config.{js,ts}', 'src/lib/api/**/*.ts']
    }
]
