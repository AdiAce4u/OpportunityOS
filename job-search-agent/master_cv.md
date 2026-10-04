# Master Curriculum Vitae

## Personal Information
- **Name**: Candidate
- **Email**: candidate@example.com
- **LinkedIn**: linkedin.com/in/candidate
- **GitHub**: github.com/candidate

---

## Projects & Technical Experience

### Distributed Key-Value Store & Raft Consensus Engine
- Engineered a distributed, fault-tolerant key-value store in Go implementing the Raft consensus protocol.
- Handled leader election, log replication, snapshotting, and network partition recovery across multi-node clusters.
- Achieved sub-5ms read/write latencies with gRPC communication and LevelDB persistent storage engine.
- Benchmarked concurrency throughput using Redis-benchmark achieving 80,000+ ops/sec.

### Microservices E-Commerce Backend & High-Throughput Payment Pipeline
- Architected RESTful and GraphQL backend microservices using Java Spring Boot, PostgreSQL, and Kafka.
- Implemented transactional outbox pattern with Redis distributed locking for idempotent payment processing.
- Containerized services with Docker and deployed on Kubernetes (EKS) with Prometheus & Grafana telemetry.
- Designed CI/CD pipeline in GitHub Actions with automated unit/integration testing and zero-downtime rolling deployments.

### High-Frequency Order Book & Execution Simulator
- Developed an ultra-low-latency L2 limit order book matching engine in modern C++ (C++20).
- Utilized lock-free ring buffers, cache-friendly data structures, and memory-mapped IPC for sub-microsecond tick-to-trade latency.
- Implemented risk checks, margin calculators, and FIX protocol adapter for exchange simulation.
- Backtested algorithmic statistical arbitrage and mean-reversion trading strategies on historical tick data.

### Large-Scale Real-Time Sentiment & Financial Risk Analytics Pipeline
- Built an end-to-end data engineering pipeline processing 2M+ daily financial filings, news, and SEC Edgar feeds.
- Orchestrated ETL workflows with Apache Spark, Kafka, and Delta Lake on Databricks.
- Extracted risk factors using NLP transformer models (BERT/FinBERT) and stored dense embeddings in Milvus vector DB.
- Built interactive analytics dashboards using FastAPI, DuckDB, and Streamlit for quantitative research teams.

### Autonomous Drone Navigation & Embedded Visual SLAM System
- Implemented real-time visual inertial SLAM and obstacle avoidance on NVIDIA Jetson Xavier and STM32 microcontroller.
- Programmed low-level motor control algorithms (PID & state-space controllers) in C/C++ with FreeRTOS.
- Integrated ROS2 / C++ nodes for LIDAR sensor fusion, Kalman filtering, and trajectory planning.
- Optimized edge computer vision inference pipelines using TensorRT achieving 60 FPS real-time detection.

### Deep Learning Multi-Modal RAG Platform & AI Agent Framework
- Built an enterprise Agentic RAG system leveraging LangChain, LlamaIndex, ChromaDB, and OpenAI/Gemini models.
- Implemented hybrid search combining sparse BM25 and dense embeddings with reciprocal rank fusion (RRF).
- Developed evaluation benchmarks using Ragas framework to measure retrieval context precision and hallucination rates.
- Packaged as a scalable asynchronous microservice with Python FastAPI and Celery workers.
