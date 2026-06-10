# Frontend Fixes and Enhancements

## Issues Fixed

### 1. Frontend-Backend Connection Error (ECONNREFUSED)

**Problem**: The frontend was showing `ECONNREFUSED` errors when trying to connect to the backend at `localhost:8000` instead of using the Docker service name `backend:8000`.

**Root Cause**: The `next.config.js` file had rewrite fallback rules that were interfering with the proper proxy setup. The Next.js route handlers at `/api/v1/[...path]/route.ts` are correctly configured to use `process.env.BACKEND_INTERNAL_URL` (which is set to `http://backend:8000` in Docker), but the fallback rewrites were causing issues.

**Solution**: 
- Removed the `rewrites()` configuration from `next.config.js`
- The Next.js route handlers (`/api/v1/[...path]/route.ts`) now handle all API proxying through `backend-proxy.ts`
- This ensures that all API calls go through the proper server-side proxy with correct Docker service resolution

**File Changed**: `frontend/next.config.js`

### 2. APK Deletion Feature

**Added**: A new delete button on the APK list with confirmation dialog

**Components Updated**:

#### `frontend/src/lib/api.ts`
- Added new function `deleteAPK(apkId: string)` that calls the backend DELETE endpoint

#### `frontend/src/components/Dashboard.tsx`
- Added imports: `Trash2` icon from lucide-react, `deleteAPK` function from api
- Added state management:
  - `deletingId`: tracks which APK is being deleted
  - `deleteConfirm`: tracks which APK deletion is being confirmed
- Added `handleDeleteAPK()` callback function that:
  - Calls the API to delete the APK
  - Refreshes the dashboard after successful deletion
  - Shows error messages on failure
- Added delete button in the APK table with:
  - Red styling to indicate destructive action
  - Trash icon for visual clarity
  - Disabled state during deletion
- Added confirmation modal dialog with:
  - Clear warning message
  - Cancel and Delete buttons
  - Loading state during deletion
  - Automatic refresh after successful deletion

**Features**:
- ✅ Confirmation dialog before deletion (prevents accidental deletion)
- ✅ Loading indicator during deletion
- ✅ Automatic list refresh after deletion
- ✅ Error handling and display
- ✅ Disabled state prevents multiple simultaneous deletions
- ✅ Backend integration with existing `/api/v1/apks/{apk_id}` DELETE endpoint

## How It Works

### Connection Flow (Fixed)
1. Frontend makes request to `/api/v1/apks`
2. Next.js route handler at `/api/v1/[...path]/route.ts` intercepts
3. Route handler calls `proxyToBackend()` from `backend-proxy.ts`
4. Backend proxy reads `process.env.BACKEND_INTERNAL_URL` (= `http://backend:8000` in Docker)
5. Request proxied to backend at correct Docker service name
6. Backend responds, response returned to frontend

### Deletion Flow
1. User clicks "Delete" button on APK row
2. Confirmation modal appears
3. User confirms deletion
4. `handleDeleteAPK()` is called
5. API call to `DELETE /api/v1/apks/{apk_id}`
6. Backend deletes APK file and database record
7. Dashboard list automatically refreshes
8. Confirmation modal closes

## Backend API

The backend already had the delete endpoint at:
```
DELETE /api/v1/apks/{apk_id}
```

Response:
```json
{
  "message": "APK deleted successfully"
}
```

The endpoint:
- Finds the APK by ID
- Deletes the physical APK file if it exists
- Deletes all related database records (cascade delete)
- Returns success message

## Testing

To test the fixes:

1. **Connection Fix**:
   - Check browser network tab - no more ECONNREFUSED errors
   - Dashboard should load APK list successfully
   - Network requests should return proper responses

2. **Delete Feature**:
   - Click "Delete" button on any APK row
   - Confirmation dialog should appear
   - Click "Delete APK" in dialog
   - List should refresh and APK should be gone
   - Click "Cancel" should close dialog without deleting

## Deployment

No additional environment variables or configuration needed. The Docker Compose setup already provides:
- `BACKEND_INTERNAL_URL: http://backend:8000` to frontend build
- Proper networking between frontend and backend containers

Just rebuild and restart the frontend container:
```bash
docker-compose down
docker-compose up --build frontend
```
