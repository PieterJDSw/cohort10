FROM vllm/vllm-openai:gemma4

RUN uv pip install --system "bitsandbytes>=0.49.2"