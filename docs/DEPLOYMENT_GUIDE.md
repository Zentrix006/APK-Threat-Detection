# Deployment and Testing Guide

## Quick Start - Rebuild and Test

### Step 1: Stop Current Containers
```bash
cd c:\Users\afx14\Desktop\APK THREAT DETECTION
docker-compose down
```

### Step 2: Rebuild Frontend
```bash
docker-compose up --build frontend -d
```

This will:
- Rebuild the frontend image with the fixed `next.config.js`
- Rebuild with `BACKEND_INTERNAL_URL=http://backend:8000` from docker-compose.yml
- Start all required services (backend, postgres, redis, ollama, nginx)

### Step 3: Verify Services Are Running
```bash
docker ps

# You should see:
# - apk-threat-postgres
# - apk-threat-redis
# - apk-threat-backend
# - apk-threat-frontend
# - apk-threat-ollama
# - apk-threat-nginx
```

### Step 4: Access the Application
- Open browser: `http://localhost:3000`
- Or: `http://localhost` (via nginx on port 80)

### Step 5: Verify Connection Fix
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Refresh the page
4. Check API calls:
   - `/health` - Should return 200 OK
   - `/api/v1/apks?limit=10` - Should return 200 with APK list
5. No more `ECONNREFUSED` errors!

## Testing Delete Functionality

### Test Case 1: Upload and Delete an APK

1. **Upload APK**:
   - Go to Dashboard
   - Drag & drop an APK file or use upload button
   - Wait for upload to complete

2. **Delete APK**:
   - Find the APK in the list
   - Click the red "Delete" button
   - Confirmation modal appears
   - Click "Delete APK" button
   - Wait for deletion (~1-2 seconds)
   - APK should disappear from list

3. **Verify Deletion**:
   - Refresh page
   - APK should still be gone
   - Check backend logs: `docker logs apk-threat-backend | tail -20`
   - Should see deletion log entry

### Test Case 2: Cancel Delete

1. Click Delete button on an APK
2. Modal appears
3. Click "Cancel" button
4. Modal closes
5. APK should still be in list

### Test Case 3: Delete Multiple APKs Sequentially

1. Upload 2 APKs
2. Delete first APK - should complete
3. Delete second APK - should complete
4. Both should be gone from list

### Test Case 4: Error Handling

1. Open browser Developer Tools
2. Go to Network tab
3. Block the delete request:
   - Right-click on DELETE request
   - Set to offline or throttle to fail
4. Click Delete
5. Error message should appear in banner
6. APK should still be in list

## Backend Verification

### Check Backend Logs
```bash
# View real-time logs
docker logs -f apk-threat-backend

# Look for successful API responses like:
# INFO:     127.0.0.1:xxxxx - "GET /api/v1/apks HTTP/1.1" 200 OK
# INFO:     127.0.0.1:xxxxx - "DELETE /api/v1/apks/xxxxxxxx HTTP/1.1" 200 OK
```

### Check Database (if needed)
```bash
# Connect to PostgreSQL
docker exec -it apk-threat-postgres psql -U apk_user -d apk_threat

# List APKs
SELECT id, filename, status FROM apk_files;

# Exit
\q
```

## Troubleshooting

### Issue: Still Getting ECONNREFUSED Errors

**Solution**:
1. Ensure all containers are running: `docker-compose ps`
2. Rebuild frontend: `docker-compose down && docker-compose up --build frontend`
3. Check container networks: `docker network ls`
4. Verify backend is healthy: `docker logs apk-threat-backend | grep "Application startup complete"`

### Issue: Delete Button Not Working

**Solution**:
1. Check browser console for errors (F12 → Console tab)
2. Check backend logs for 404 or 500 errors
3. Verify APK ID is valid: `docker logs apk-threat-backend | grep DELETE`
4. Try refreshing page and trying again

### Issue: Deletion Completes But List Doesn't Refresh

**Solution**:
1. Manually refresh page with F5
2. Check browser Network tab for failed requests
3. Check backend logs for errors
4. Clear browser cache and try again

### Issue: Modal Appears Behind Content

**Solution**:
1. Check browser zoom level (Ctrl+0 to reset)
2. Clear browser cache
3. Try in incognito/private mode
4. Update browser to latest version

## Performance Monitoring

### Monitor Dashboard Load Time
```
1. Open DevTools (F12)
2. Go to Performance tab
3. Click record
4. Refresh page
5. Stop recording
6. Check timeline for slow operations
```

### Expected Performance
- Dashboard load: < 1 second
- APK list fetch: < 500ms
- Delete operation: < 2 seconds
- Delete confirmation modal: Instant

## Verification Checklist

- [ ] All Docker containers are running
- [ ] Browser can access `http://localhost:3000`
- [ ] Dashboard loads without errors
- [ ] APK list displays properly
- [ ] Delete button is visible on each row
- [ ] Clicking delete shows confirmation modal
- [ ] Confirming delete removes APK from list
- [ ] Canceling delete keeps APK in list
- [ ] Refreshing page after delete keeps it deleted
- [ ] Error messages display properly
- [ ] Loading indicators show during operations
- [ ] No console errors in browser DevTools

## File Changes Summary

### Modified Files
1. **frontend/next.config.js**
   - Removed: `async rewrites()` method
   - Reason: Was interfering with server-side proxy

2. **frontend/src/lib/api.ts**
   - Added: `deleteAPK(apkId)` function
   - Reason: Provides API client for delete operation

3. **frontend/src/components/Dashboard.tsx**
   - Added: Delete button to APK table
   - Added: Confirmation modal
   - Added: Delete state management
   - Reason: User interface for deletion

### Backend
- No changes needed
- Already has DELETE endpoint at `/api/v1/apks/{apk_id}`

## Rolling Back Changes

If issues occur, you can revert to the previous version:

### Option 1: Revert Files
```bash
# Restore from git
git checkout frontend/next.config.js
git checkout frontend/src/lib/api.ts
git checkout frontend/src/components/Dashboard.tsx

# Rebuild
docker-compose up --build frontend
```

### Option 2: Manual Revert
Restore the original files from backups if available

## Next Steps

After verifying everything works:

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Fix frontend-backend connection and add APK deletion feature"
   git push origin main
   ```

2. **Deploy to Production** (if applicable)
   - Update production environment
   - Run smoke tests
   - Monitor logs for issues

3. **Consider Enhancements**
   - Add batch delete functionality
   - Implement search/filter
   - Add export functionality
   - Improve error messages

## Support

For issues or questions:
1. Check logs: `docker logs <container-name>`
2. Check browser DevTools: F12
3. Review error messages carefully
4. Try in different browser
5. Clear cache and retry

## Contact

For technical support, refer to PROJECT_SUMMARY.md or CONTRIBUTING.md
