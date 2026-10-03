# Endless Storage Frontend

This is the frontend client for the **Endless Storage** platform, a cloud storage abstraction that pools multiple Google Drive accounts together into a single, seamless virtual drive.

The frontend is built with **Next.js 16 (App Router)**, **React 19**, and **Tailwind CSS v4**, using **Bun** as the package manager and JavaScript runtime.

## ✨ Features

- **Modern Drive UI**: A sleek, intuitive file manager interface that mimics native desktop or cloud storage experiences.
- **Client-Side File Processing**: Leverages `streamsaver` and `fflate` to efficiently handle file streams and zipped downloads directly in the browser.
- **Progress Tracking**: Real-time progress bars and status updates for large multi-chunk uploads.
- **Toast Notifications**: Built with `sonner` for elegant, non-intrusive feedback on file operations (uploads, deletions, migrations).
- **Responsive Design**: Fully styled using the latest Tailwind CSS v4 engine for a fluid experience on any screen size.

## 🚀 Technologies

- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS v4
- **Icons**: Lucide React
- **Package Manager & Runtime**: Bun

---

## 🛠️ Complete Setup Instructions

### 1. Environment Setup
Make sure you have [Bun](https://bun.sh/) installed.

```bash
# Clone the repository and enter the frontend directory
cd frontend

# Install dependencies using Bun
bun install
```

### 2. Configuration (`.env.local`)
Create a `.env.local` file in the root of the frontend directory. If there's an `.env.example`, you can copy it.

```env
# Example: The URL where your FastAPI backend is running
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Running the Application

Start the development server with Bun:

```bash
bun dev
```
Your application will be running at `http://localhost:3000`.

---

## 🧑‍💻 Architecture & Project Structure

- **`app/`**: Next.js App Router structure.
  - `page.tsx`: The main landing or root page.
  - `drive/`: The core file manager application routes.
- **`components/`**: Reusable React components.
  - `drive/`: Components specific to the file manager (e.g., `Header.tsx`, file lists, modals).
- **`lib/`**: Utility functions, API clients, and shared logic.
- **`public/`**: Static assets like icons and images.
