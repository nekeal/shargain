import { defaultPlugins, defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
    input: './openapi.json',
    output: 'src/lib/api',
    plugins: [
        ...defaultPlugins,
        {
            name: '@hey-api/client-fetch',
            throwOnError: true,
        },
    ],
});
