# 5. Scan

Enables food recognition via photo upload. The scan service uses AI-based image recognition to identify food items and return nutritional data, which can then be logged to the user's daily food log.

## Endpoints

| Method | Endpoint | Description | Auth | Docs |
| --- | --- | --- | --- | --- |
| POST | `/scan` | Upload a food photo for recognition | Yes | [upload-scan.md](upload-scan.md) |
| POST | `/scan/log` | Save recognized food to the user's food log | Yes | [log-scan.md](log-scan.md) |

## Implementation Notes

- Image analysis is performed server-side via AI-based food recognition (image classification / OCR).
- The scan result includes confidence scores for each identified food item.
- After reviewing the recognition results, the client can call the log endpoint to persist the items.
- All endpoints require JWT authentication.
