# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: Shargain API
  version: 1.0.0
  description: API for the Shargain platform
servers:
  - url: /api/public
    description: Public API

paths:
  /auth/login:
    post:
      summary: Login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: OK
  /auth/logout:
    post:
      summary: Logout
      responses:
        '200':
          description: OK
  /auth/signup:
    post:
      summary: Signup
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                email:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: OK
  /auth/csrf:
    get:
      summary: Get CSRF token
      responses:
        '200':
          description: OK
  /me:
    get:
      summary: Get current user
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /targets:
    get:
      summary: Get all scrapping targets
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ScrappingTarget'
    post:
      summary: Create a scrapping target
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ScrappingTarget'
      responses:
        '201':
          description: Created
  /targets/{id}:
    get:
      summary: Get a scrapping target
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScrappingTarget'
    put:
      summary: Update a scrapping target
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ScrappingTarget'
      responses:
        '200':
          description: OK
    delete:
      summary: Delete a scrapping target
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: No Content
  /notifications:
    get:
      summary: Get all notification configs
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/NotificationConfig'
    post:
      summary: Create a notification config
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NotificationConfig'
      responses:
        '201':
          description: Created
  /notifications/{id}:
    get:
      summary: Get a notification config
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotificationConfig'
    put:
      summary: Update a notification config
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NotificationConfig'
      responses:
        '200':
          description: OK
    delete:
      summary: Delete a notification config
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: No Content

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        username:
          type: string
        email:
          type: string
        tier:
          type: string
    ScrappingTarget:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        enable_notifications:
          type: boolean
        is_active:
          type: boolean
        notification_config:
          type: integer
          nullable: true
        owner:
          type: string
          format: uuid
        scraping_urls:
          type: array
          items:
            $ref: '#/components/schemas/ScrapingUrl'
    ScrapingUrl:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        url:
          type: string
        is_active:
          type: boolean
        scraping_target:
          type: integer
    NotificationConfig:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        channel:
          type: string
          enum:
            - discord
            - telegram
        register_token:
          type: string
        owner:
          type: string
          format: uuid
```
