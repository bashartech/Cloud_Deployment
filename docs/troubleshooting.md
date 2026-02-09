# Troubleshooting Guide for Todo AI Chatbot

## Common Issues and Solutions

### ChatKit Domain Issues

#### Issue: "Blocked by CORS policy" error
**Symptoms**: Browser console shows CORS errors when using the chat interface
**Solution**:
1. Add your domain to the ChatKit domain allowlist
2. For local development: `http://localhost:3000`
3. For production: your actual domain

#### Issue: Chat interface doesn't load
**Symptoms**: Chat window is blank or shows loading spinner indefinitely
**Solution**:
1. Check if ChatKit domain is properly configured
2. Verify that the chat components are imported correctly
3. Ensure the FloatingChatbot component is added to your layout

### Authentication Issues

#### Issue: Unauthorized access to chat endpoints
**Symptoms**: HTTP 401/403 errors when trying to chat
**Solution**:
1. Verify JWT token is properly included in requests
2. Check that user is authenticated before accessing chat
3. Ensure session is valid and not expired

#### Issue: User session expires during chat
**Symptoms**: Suddenly unable to send messages mid-conversation
**Solution**:
1. Implement proper session refresh mechanism
2. Check JWT expiration times
3. Ensure proper error handling for expired tokens

### MCP Server Issues

#### Issue: MCP server not connecting to backend
**Symptoms**: Chat responses fail or show "connection error"
**Solution**:
1. Verify MCP server is running
2. Check `MCP_SERVER_URL` environment variable
3. Ensure backend is accessible from MCP server
4. Verify authentication headers are properly passed

#### Issue: MCP tools not responding
**Symptoms**: AI agent doesn't perform task operations
**Solution**:
1. Check that MCP tools are properly registered
2. Verify tool contracts match the specification
3. Ensure X-User-ID header is properly passed to backend

### Database Issues

#### Issue: Database connection failures
**Symptoms**: HTTP 500 errors, inability to save/load conversations
**Solution**:
1. Verify `DATABASE_URL` environment variable
2. Check database credentials and permissions
3. Ensure database is running and accessible

#### Issue: User data isolation not working
**Symptoms**: Users can see other users' tasks or conversations
**Solution**:
1. Verify user_id scoping in all database queries
2. Check that authentication is validated before DB access
3. Ensure proper foreign key relationships

### Performance Issues

#### Issue: Slow chat responses
**Symptoms**: Long delays between sending message and receiving response
**Solution**:
1. Check network connectivity between components
2. Verify MCP server performance
3. Monitor database query performance
4. Consider implementing caching where appropriate

#### Issue: Rate limiting too restrictive
**Symptoms**: Users frequently hit rate limits
**Solution**:
1. Adjust rate limit parameters in `/backend/routes/chat.py`
2. Consider implementing sliding window rate limiting
3. Add user-specific rate limits vs IP-based limits

### Agent Issues

#### Issue: AI agent doesn't understand commands
**Symptoms**: Agent responds with "I don't understand" to valid commands
**Solution**:
1. Verify natural language command mappings
2. Check that MCP tools are properly configured
3. Ensure agent has proper instructions for task operations

#### Issue: Tool calls not executing
**Symptoms**: Agent says it will perform action but nothing happens
**Solution**:
1. Verify MCP tool contracts match specification
2. Check that backend task APIs are working
3. Ensure proper authentication is passed to backend

## Debugging Steps

### Frontend Debugging
1. Open browser developer tools
2. Check Console tab for JavaScript errors
3. Check Network tab for failed API requests
4. Verify that auth session is present in cookies/localStorage

### Backend Debugging
1. Check application logs
2. Verify environment variables are set correctly
3. Test API endpoints directly with curl/postman
4. Check database connectivity

### MCP Server Debugging
1. Check MCP server logs
2. Verify tool registration
3. Test direct connections between MCP and backend
4. Check authentication flows

## Error Codes Reference

- `401 Unauthorized`: User not authenticated
- `403 Forbidden`: User lacks permission for requested resource
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error occurred
- `503 Service Unavailable`: Dependency (DB/MCP) not available

## Logging and Monitoring

### Log Levels
- `INFO`: Normal operations and user actions
- `WARNING`: Potential issues or unusual events
- `ERROR`: Errors that don't prevent operation
- `CRITICAL`: Errors that prevent operation

### Sensitive Data Protection
- Never log full JWT tokens
- Mask user IDs in logs (e.g., "user_***abc123")
- Don't log personal information or task content

## Support Resources

### For Developers
- Check the `/specs/` directory for detailed API contracts
- Review the agent behavior specification
- Look at the MCP tool specifications

### For Users
- Clear browser cache and cookies if experiencing issues
- Refresh the page if chat interface stops responding
- Contact support if issues persist after troubleshooting

## When to Escalate

Escalate to senior developers when:
- Database corruption is suspected
- Production security issues are identified
- Performance issues persist after optimization
- MCP server architecture needs changes