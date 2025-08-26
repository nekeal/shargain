export default {
    client: '@hey-api/client-fetch', // or '@hey-api/client-axios'
    input: './openapi.json',
    output: './src/lib/api',
    services: {
        // …
    },
    // 👇 the important part
    clientOptions: {
        throwOnError: true,
    },
};
