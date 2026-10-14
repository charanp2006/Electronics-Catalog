# 10. Test Plan

## 10.1 Testing Objectives
Verify functionality, data integrity, API correctness, and end-to-end flow.

## 10.2 Test Scope
- Product listing, search, filter, sort
- Product detail retrieval
- API endpoints
- Frontend rendering
- MongoDB data operations
- Connection (local/Atlas)

## 10.3 Test Types
- Manual API testing (Swagger/curl)
- Frontend UI testing
- Integration testing (API + DB)
- Data validation

## 10.4 Test Cases

| Test ID | Description | Expected | Status |
|---|---|---|---|
| TC-001 | GET /products returns list | 200 OK, array of products | Pass |
| TC-002 | Search with query returns filtered | Matches name/brand | Pass |
| TC-003 | Filter by category works | Correct subset | Pass |
| TC-004 | Price range filter works | Within range | Pass |
| TC-005 | Sort by price_asc works | Ascending order | Pass |
| TC-006 | GET /products/{slug} valid | 200 with full details | Pass |
| TC-007 | GET /products/{invalid} | 404 Not Found | Pass |
| TC-008 | Frontend loads products | Grid renders | Pass |
| TC-009 | Search from UI works | Results update | Pass |
| TC-010 | MongoDB seeded data present | Correct counts | Pass |

## 10.5 API Test Examples (curl)

```bash
# List products
curl http://localhost:8000/api/v1/products

# Search
curl http://localhost:8000/api/v1/products?q=samsung

# Filter by category
curl http://localhost:8000/api/v1/products?category=smartphones

# Product detail
curl http://localhost:8000/api/v1/products/samsung-galaxy-s24
```

## 10.6 Validation Checklist

- [x] All required collections exist in MongoDB
- [x] Seed data matches expected counts
- [x] API returns correct JSON structure
- [x] Frontend fetches without CORS errors
- [x] No console errors
- [x] Local environment tested (Atlas pending credentials)

## 10.7 Automated Tests

`backend/tests/` contains 23 `pytest` tests covering products, auth, cart,
wishlist, reviews and orders. Run with:

```bash
cd backend
.venv\Scripts\activate
pytest
```

```mermaid
flowchart LR
    A[Unit Tests - Manual] --> B[API Tests]
    B --> C[Integration Tests]
    C --> D[UI Tests]
    D --> E[End-to-End Validation]
```
