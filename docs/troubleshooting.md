# Invisible Art Gallery - Troubleshooting Guide

This document provides solutions for common issues you might encounter while developing or using the Invisible Art Gallery platform.

## Development Setup Issues

### Database Connection Problems

**Issue**: Unable to connect to PostgreSQL database.

**Solution**:
1. Ensure PostgreSQL is running:
   ```bash
   # Windows
   sc query postgresql
   
   # Linux/macOS
   sudo systemctl status postgresql
   ```
2. Verify your database credentials in `.env` file
3. Check that the database has been created:
   ```bash
   psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='invisible_art_gallery';"
   ```
4. If database doesn't exist, create it:
   ```bash
   createdb -U postgres invisible_art_gallery
   ```

### Django Migrations Failing

**Issue**: Django migrations fail to apply.

**Solution**:
1. Reset migrations (if in development):
   ```bash
   python manage.py migrate --fake accounts zero
   python manage.py migrate --fake artworks zero
   # Delete migration files except __init__.py
   python manage.py makemigrations
   python manage.py migrate --fake-initial
   ```
2. Check for database schema conflicts

### React Development Server Issues

**Issue**: React development server fails to start.

**Solution**:
1. Check for port conflicts:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   
   # Linux/macOS
   lsof -i :3000
   ```
2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```
3. Remove `node_modules` and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```

## Authentication Issues

### JWT Token Problems

**Issue**: JWT token authentication fails.

**Solution**:
1. Check token expiration time (default is 1 hour)
2. Ensure `SECRET_KEY` in Django settings matches the key used to generate the token
3. Verify that the token is properly formatted in the Authorization header:
   ```
   Authorization: Bearer <token>
   ```
4. Try refreshing the token using the refresh endpoint

### CORS Issues

**Issue**: CORS errors when making API requests from frontend.

**Solution**:
1. Check CORS settings in Django:
   ```python
   # settings.py
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
   ]
   
   CORS_ALLOW_CREDENTIALS = True
   ```
2. Ensure proper headers are set in frontend API calls

## WebSocket Connection Issues

### Connection Failures

**Issue**: Unable to establish WebSocket connection.

**Solution**:
1. Verify Redis is running (required for Django Channels):
   ```bash
   # Windows
   sc query redis
   
   # Linux/macOS
   sudo systemctl status redis
   ```
2. Check WebSocket URL format and authentication token
3. Ensure ASGI configuration is correct in `asgi.py`
4. Look for WebSocket connection logs in browser console

### Message Not Received

**Issue**: Real-time updates not being received.

**Solution**:
1. Check channel subscription in frontend:
   ```javascript
   socket.send(JSON.stringify({
     command: 'subscribe',
     identifier: JSON.stringify({
       channel: 'ArtworkChannel',
       artwork_id: '550e8400-e29b-41d4-a716-446655440001'
     })
   }));
   ```
2. Verify WebSocket consumer implementation in backend
3. Check for errors in Django logs

## Encryption/Decryption Issues

### File Encryption Failures

**Issue**: Unable to encrypt artwork files.

**Solution**:
1. Check for proper installation of cryptography libraries:
   ```bash
   pip install cryptography
   ```
2. Verify file permissions for temporary files
3. Ensure encryption keys are properly generated and stored

### Decryption Problems

**Issue**: Artwork doesn't reveal properly when conditions are met.

**Solution**:
1. Check condition logic in `artworks/views.py`
2. Verify that condition checks are being executed
3. Look for errors in decryption service
4. Check for WebSocket message delivery failures

## Docker Issues

### Container Startup Failures

**Issue**: Docker containers fail to start properly.

**Solution**:
1. Check Docker logs:
   ```bash
   docker logs invisible-art-gallery-backend
   docker logs invisible-art-gallery-frontend
   ```
2. Ensure `.env` files are properly mounted
3. Verify network configuration in `docker-compose.yml`
4. Make sure required ports are not in use

### Volume Permission Issues

**Issue**: Permission denied errors in Docker volumes.

**Solution**:
1. Check ownership of mounted volumes:
   ```bash
   ls -la /path/to/mounted/volume
   ```
2. Set appropriate permissions:
   ```bash
   sudo chown -R 1000:1000 /path/to/mounted/volume
   ```

## Other Common Issues

### Large File Uploads

**Issue**: Large artwork files fail to upload.

**Solution**:
1. Check file size limits in Django settings:
   ```python
   # settings.py
   DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
   ```
2. Configure Nginx/web server for large file uploads:
   ```nginx
   # nginx.conf
   client_max_body_size 20M;
   ```
3. Increase timeout settings for slow uploads

### Performance Issues

**Issue**: Slow response times for artwork viewing.

**Solution**:
1. Implement caching for non-dynamic content:
   ```python
   # settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```
2. Consider CDN for serving artwork images
3. Optimize database queries in views

### AR.js Integration Issues

**Issue**: AR features not working properly.

**Solution**:
1. Check browser compatibility (WebXR support)
2. Verify camera permissions are granted
3. Check AR.js library imports and versions
4. Test on a device with proper AR capabilities

## Getting Further Help

If you're still experiencing issues:

1. Check the GitHub repository issues section
2. Consult the Django and React documentation
3. Search for specific error messages on Stack Overflow
4. Reach out to the development team at support@invisibleartgallery.com 