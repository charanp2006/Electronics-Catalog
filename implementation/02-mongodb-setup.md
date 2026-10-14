# Implementation Plan - 02: MongoDB Setup

## Objectives
- Install/test local MongoDB
- Setup MongoDB Atlas (free tier)
- Test connections
- Document both approaches

## Tasks

### A. Local MongoDB
1. Download MongoDB Community Server
2. Install & start `mongod`
3. Test with `mongosh`: `mongosh "mongodb://localhost:27017"`
4. Create DB: `electrohub_nosql`
5. Test CRUD in shell

### B. MongoDB Compass
1. Install Compass
2. Connect to local: `mongodb://localhost:27017`
3. Explore collections

### C. MongoDB Atlas
1. Create account at mongodb.com
2. Create free M0 cluster
3. Database Access: create user
4. Network Access: Add IP (0.0.0.0/0 for dev OR current IP)
5. Get SRV connection string
6. Test in Compass

### D. Environment Config
1. Create `backend/.env.example`
2. Add both URIs + toggle
3. Verify switch logic

## Verification
- [ ] mongosh connects locally
- [ ] Compass shows DB
- [ ] Atlas connects from Compass
- [ ] Both URIs tested
