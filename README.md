# Real-Time Chat Application with WebSockets

## Project Summary
This project involves designing and documenting a real-time chat application using WebSockets, Python, and Kafka. The goal is to practice client-server patterns, real-time messaging, state management, and architectural decision-making.

## Objectives
- **Real-time Messaging**: Support for public and private rooms.
- **Persistence**: Store messages in a Postgres database (Supabase).
- **History**: Paginable message history.
- **Notifications**: Real-time alerts for user join/leave events.
- **Authentication**: Basic JWT authentication and room access control.

## Requirements

### Functional
1.  **Connection**: User authentication via JWT.
2.  **Room Management**: Create, join, and leave chat rooms.
3.  **Messaging**: Send and receive messages in real-time via WebSockets.
4.  **Persistence**: Save messages to a Supabase Postgres database.
5.  **History**: Retrieve message history with pagination (REST API).
6.  **Notifications**: Notify users of room membership changes.
7.  **Access Control**: Support for public and private (invite/password) rooms.

### Non-Functional
-   **Concurrency**: Support tens of simultaneous users (PoC).
-   **Latencia**: Message delivery < 850 ms.
-   **Durability**: Confirmed messages are persisted.
-   **Observability**: Basic metrics (connections, latency) and logs.
-   **Deployment**: Docker Compose for development.

## Architecture
The system follows a modular architecture:

-   **Client Web**: User Interface (Frontend).
-   **API Gateway / Auth REST**: Handles login, history, and room creation.
-   **WebSocket Server**: Manages connections, broadcasts messages, and validates permissions.
-   **Broker (Kafka)**: Message intermediary for decoupling and scalability.
-   **Database (Supabase Postgres)**: Stores `users`, `rooms`, `messages`, and `room_members`.
-   **Cache (Optional)**: Redis for pub/sub and session sharing.

## Technology Stack
-   **Backend**: Python (FastAPI/AIOHTTP recommended for Async support).
-   **Broker**: Apache Kafka.
-   **Database**: PostgreSQL (Supabase).
-   **Containerization**: Docker & Docker Compose.
