# 12. Netlify Deployment (Frontend)

This project is full-stack. **Netlify hosts only the React frontend** (static build). The FastAPI backend must run on a separate host (Render, Railway, Hugging Face Spaces, a VPS, or any Python host) and MongoDB must be Atlas, since Netlify has no Python runtime. See [13. Backend + MongoDB Atlas](13-backend-and-atlas-deployment.md) for exactly how to set up the backend and Atlas.
