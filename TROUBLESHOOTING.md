# ThreeJS RAG Generator - Troubleshooting Guide

## How to Reset the App When It Stops Working

### Quick Reset Steps

1. **Stop the Server**
   ```bash
   # Kill all uvicorn processes
   pkill -f uvicorn
   # Or find and kill specific process
   ps aux | grep uvicorn
   kill -9 [PROCESS_ID]
   ```

2. **Check for File Corruption**
   ```bash
   # Check if main files exist and have content
   ls -la main.py app/anthropic_client.py
   head -5 main.py app/anthropic_client.py
   ```

3. **Restart the Server**
   ```bash
   cd /home/musamaclaude/threejs-rag-generator
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
   ```

4. **Check Server Status**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

### Common Issues and Solutions

#### 1. Import Error (Cannot import ClaudeClient)
**Symptoms:** Server won't start, ImportError in logs
**Solution:**
```bash
# Check if class exists in file
grep -n "class ClaudeClient" app/anthropic_client.py
# If missing, restore from backup or rebuild
```

#### 2. Safety Filter Blocking
**Symptoms:** 500 errors, "Response blocked by safety filters"
**Solution:**
```bash
# Switch to different model or adjust safety settings
# Edit app/anthropic_client.py and change model to 'gemini-2.0-flash-exp'
```

#### 3. API Key Issues
**Symptoms:** "ANTHROPIC_API_KEY not set" error
**Solution:**
```bash
# Check if API key is set
cat .env.example
# Should contain: ANTHROPIC_API_KEY=your_key_here
```

#### 4. Port Already in Use
**Symptoms:** "Address already in use" error
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 [PID]
# Or use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

#### 5. ChromaDB Database Issues
**Symptoms:** Database errors, indexing failures
**Solution:**
```bash
# Reset the vector database
rm -rf chroma_db/
python3 index_dataset.py
```

### Complete Reset (Nuclear Option)

If all else fails, here's how to completely reset:

```bash
# 1. Stop all processes
pkill -f uvicorn

# 2. Clean up
rm -rf chroma_db/ server.log

# 3. Check core files
ls -la main.py app/anthropic_client.py rag/rag_engine.py

# 4. Reinstall dependencies (if needed)
pip3 install --upgrade fastapi uvicorn python-multipart pydantic google-generativeai chromadb python-dotenv

# 5. Re-index dataset
python3 index_dataset.py

# 6. Restart server
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

# 7. Test
curl http://localhost:8000/health
```

### Monitoring and Logs

#### Check Server Logs
```bash
tail -f server.log
```

#### Check for Running Processes
```bash
ps aux | grep uvicorn
ps aux | grep python
```

#### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Simple generation test
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple cube", "temperature": 0.7}'
```

### File Structure Check

Ensure these files exist and have proper content:
```
threejs-rag-generator/
├── main.py                 # FastAPI app
├── .env.example           # API keys
├── requirements.txt       # Dependencies
├── index_dataset.py       # Indexing script
├── app/
│   ├── __init__.py
│   └── anthropic_client.py   # AI client
├── rag/
│   ├── __init__.py
│   └── rag_engine.py      # Vector search
└── dataset/
    └── threejs_all_vertex.jsonl  # Training data
```

### Prevention Tips

1. **Regular Backups**: Copy working versions of key files
2. **Monitor Logs**: Keep an eye on server.log for errors
3. **Test After Changes**: Always test API after modifications
4. **Use Version Control**: Git track your changes
5. **Resource Monitoring**: Check memory/CPU usage

### Emergency Contacts

- Check GitHub issues: https://github.com/anthropics/claude-code/issues
- FastAPI docs: https://fastapi.tiangolo.com/
- Three.js docs: https://threejs.org/docs/

### Quick Health Check Script

Create `health_check.sh`:
```bash
#!/bin/bash
echo "=== ThreeJS RAG Generator Health Check ==="
echo "1. Checking server process..."
ps aux | grep uvicorn | grep -v grep || echo "❌ Server not running"

echo "2. Checking API response..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ API responding" || echo "❌ API not responding"

echo "3. Checking files..."
[ -f main.py ] && echo "✅ main.py exists" || echo "❌ main.py missing"
[ -f app/anthropic_client.py ] && echo "✅ anthropic_client.py exists" || echo "❌ anthropic_client.py missing"

echo "4. Checking database..."
[ -d chroma_db ] && echo "✅ Database exists" || echo "❌ Database missing"

echo "=== End Health Check ==="
```

Run with: `chmod +x health_check.sh && ./health_check.sh`