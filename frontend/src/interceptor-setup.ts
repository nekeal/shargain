import { client } from "./lib/api/client.gen";

client.interceptors.request.use((request) => {
    const csrfToken = sessionStorage.getItem('csrfToken');
    if (csrfToken) {
      request.headers.set('X-CSRFToken', csrfToken);
    }
    return request;
  });
