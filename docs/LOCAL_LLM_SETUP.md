# Local LLM Setup Guide

This guide covers how to set up and use locally hosted LLMs with your AI Scheduling Agent, eliminating the need for external API calls and costs.

## 🏗️ Deployment Options

### 1. **Ollama** (Recommended for Beginners)
**Best for:** Easy setup, good performance, wide model support
**Hardware:** 8GB+ RAM, decent CPU/GPU

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose one)
ollama pull llama2:7b        # 4GB RAM, good performance
ollama pull llama2:13b       # 8GB RAM, better performance  
ollama pull codellama:7b     # 4GB RAM, code-focused
ollama pull mistral:7b       # 4GB RAM, excellent performance
ollama pull phi:2.7b         # 2GB RAM, lightweight

# Start Ollama server
ollama serve
```

### 2. **vLLM** (High Performance)
**Best for:** Production deployments, high throughput
**Hardware:** 16GB+ RAM, NVIDIA GPU recommended

```bash
# Install vLLM
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --host 0.0.0.0 \
    --port 8000
```

### 3. **LM Studio** (GUI Option)
**Best for:** Windows users, easy model management
**Hardware:** 8GB+ RAM

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Download models through the GUI
3. Start local server on port 1234

### 4. **Text Generation WebUI** (Advanced)
**Best for:** Model experimentation, multiple models
**Hardware:** 8GB+ RAM, GPU optional

```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
python server.py --api --listen
```

## 🔧 Configuration

### Environment Setup

Update your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=local

# Local LLM Configuration
LOCAL_LLM_HOST=localhost
LOCAL_LLM_PORT=11434  # Ollama default
LOCAL_LLM_MODEL=llama2:7b
LOCAL_LLM_TYPE=ollama
```

### Model Recommendations

| Use Case | Model | Size | RAM | Performance |
|----------|-------|------|-----|-------------|
| **Development/Testing** | `phi:2.7b` | 2GB | 4GB | ⭐⭐⭐ |
| **General Purpose** | `llama2:7b` | 4GB | 8GB | ⭐⭐⭐⭐ |
| **Better Quality** | `llama2:13b` | 7GB | 16GB | ⭐⭐⭐⭐⭐ |
| **Code Focused** | `codellama:7b` | 4GB | 8GB | ⭐⭐⭐⭐ |
| **Best Performance** | `mistral:7b` | 4GB | 8GB | ⭐⭐⭐⭐⭐ |

## 🚀 Quick Start

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull a Model
```bash
ollama pull llama2:7b
```

### 3. Start Ollama
```bash
ollama serve
```

### 4. Update Your App
```bash
# In your backend directory
echo "LLM_PROVIDER=local" >> .env
echo "LOCAL_LLM_MODEL=llama2:7b" >> .env
```

### 5. Restart Your Backend
```bash
uvicorn main:app --reload
```

## 🏢 Enterprise Deployment Options

### 1. **Self-Hosted with Docker**

```dockerfile
# Dockerfile for Ollama
FROM ollama/ollama:latest
EXPOSE 11434
CMD ["ollama", "serve"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  scheduling-agent:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=local
      - LOCAL_LLM_HOST=ollama
      - LOCAL_LLM_PORT=11434
    depends_on:
      - ollama

volumes:
  ollama_data:
```

### 2. **Kubernetes Deployment**

```yaml
# k8s-ollama.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

### 3. **Cloud Deployment**

#### AWS with EC2
```bash
# Launch EC2 instance (g4dn.xlarge or larger)
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type g4dn.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxxxxxxxx

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2:7b
ollama serve
```

#### Google Cloud with GCE
```bash
# Create instance with GPU
gcloud compute instances create ollama-instance \
  --machine-type n1-standard-4 \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud

# Install and run Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2:7b
ollama serve
```

## 📊 Performance Comparison

| Provider | Cost | Latency | Privacy | Setup Complexity |
|----------|------|---------|---------|------------------|
| **OpenAI API** | $0.002/1K tokens | 1-3s | ❌ | ⭐ |
| **Gemini API** | $0.0005/1K tokens | 2-5s | ❌ | ⭐ |
| **Local Ollama** | $0 | 5-15s | ✅ | ⭐⭐ |
| **Local vLLM** | $0 | 2-8s | ✅ | ⭐⭐⭐ |

## 🔒 Security Benefits

### Privacy
- **No data leaves your infrastructure**
- **No API key management**
- **No usage tracking**
- **Compliance with data regulations**

### Cost Control
- **No per-token charges**
- **Predictable infrastructure costs**
- **No rate limiting**
- **No quota exhaustion**

## 🛠️ Troubleshooting

### Common Issues

1. **Model not found**
```bash
# Check available models
ollama list

# Pull the model
ollama pull llama2:7b
```

2. **Out of memory**
```bash
# Use smaller model
ollama pull phi:2.7b

# Or increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. **Slow performance**
```bash
# Use GPU acceleration (if available)
nvidia-smi  # Check GPU
ollama run llama2:7b --gpu

# Or use quantized model
ollama pull llama2:7b-q4_0
```

### Performance Optimization

1. **Model Quantization**
```bash
# Use quantized models for better performance
ollama pull llama2:7b-q4_0  # 4-bit quantization
ollama pull llama2:7b-q8_0  # 8-bit quantization
```

2. **GPU Acceleration**
```bash
# Install NVIDIA drivers and CUDA
# Then use GPU flag
ollama run llama2:7b --gpu
```

3. **Memory Optimization**
```bash
# Set memory limits
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*
ollama serve --memory 8192
```

## 🎯 Best Practices

### 1. **Model Selection**
- Start with smaller models for development
- Use quantized models for production
- Match model size to available hardware

### 2. **Infrastructure**
- Use dedicated servers for production
- Implement proper monitoring
- Set up automated backups

### 3. **Security**
- Run behind reverse proxy
- Implement authentication
- Use HTTPS in production

### 4. **Monitoring**
```bash
# Monitor Ollama
curl http://localhost:11434/api/tags

# Check resource usage
htop
nvidia-smi  # if using GPU
```

## 🔄 Migration from Cloud APIs

### Step 1: Install Local LLM
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2:7b
```

### Step 2: Update Configuration
```bash
# Change from
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key

# To
LLM_PROVIDER=local
LOCAL_LLM_MODEL=llama2:7b
```

### Step 3: Test and Optimize
```bash
# Test performance
curl -X POST http://localhost:8000/api/v1/schedule \
  -H "Content-Type: application/json" \
  -d '{"request_text": "Schedule a meeting tomorrow at 2 PM"}'
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer with multiple Ollama instances
- Implement model serving with vLLM
- Use Kubernetes for orchestration

### Vertical Scaling
- Upgrade to larger models
- Add more GPU resources
- Optimize model quantization

### Hybrid Approach
- Use local models for sensitive data
- Use cloud APIs for high-volume, non-sensitive tasks
- Implement intelligent routing based on data sensitivity

This setup gives you complete control over your AI infrastructure while maintaining the same functionality as cloud APIs! 