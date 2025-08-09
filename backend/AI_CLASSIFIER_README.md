# AI-Powered Annual Report Classifier

This module provides AI-powered classification for determining if a document is an annual report or financial statement using a local 8B Llama model.

## Features

- **AI-powered classification**: Uses local Llama-2-7b-chat-hf model for document classification
- **Fallback classification**: Rule-based classification when AI is not available
- **Batch processing**: Classify multiple documents at once
- **Configurable**: JSON-based configuration for model and classification parameters
- **Confidence scoring**: Provides confidence scores for classification decisions
- **Integration**: Seamlessly integrates with existing collector.py pipeline

## Installation

### Prerequisites

1. Python 3.8+
2. PyTorch (for AI functionality)
3. Transformers library

### Dependencies

Install the required dependencies:

```bash
pip install torch transformers accelerate sentencepiece
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

## Configuration

The AI classifier uses a JSON configuration file (`ai_config.json`) for customization:

```json
{
    "model_config": {
        "model_name": "meta-llama/Llama-2-7b-chat-hf",
        "device": "auto",
        "max_tokens": 50,
        "temperature": 0.1,
        "trust_remote_code": true,
        "use_fast_tokenizer": false
    },
    "classification_config": {
        "max_content_chars": 2000,
        "max_pages_to_extract": 5,
        "confidence_threshold": 60,
        "fallback_enabled": true
    },
    "prompts": {
        "classification_prompt": "...",
        "confidence_prompt": "..."
    },
    "fallback_indicators": {
        "positive": ["annual report", "financial statements", ...],
        "negative": ["interim", "quarter", ...]
    }
}
```

## Usage

### Basic Usage

```python
from ai_classifier import classify_document, classify_batch

# Classify a single document
result = classify_document("path/to/document.pdf")
print(f"Is annual report: {result['is_annual_report']}")
print(f"Confidence: {result['confidence']}%")
print(f"Reasoning: {result['reasoning']}")

# Classify multiple documents
results = classify_batch(["doc1.pdf", "doc2.pdf", "doc3.pdf"])
for result in results:
    print(f"{result['pdf_path']}: {result['is_annual_report']} ({result['confidence']}%)")
```

### Integration with Collector

The AI classifier is automatically integrated into the existing `collector.py` pipeline:

1. **Enhanced scoring**: `compute_financial_report_score()` now uses AI classification when available
2. **Improved validation**: `is_likely_financial_report()` uses AI confidence scores
3. **Fallback support**: Falls back to heuristic classification when AI is not available

### API Endpoints

New API endpoints are available for AI classification:

- `POST /api/ai/classify` - Classify a single document
- `POST /api/ai/classify_batch` - Classify multiple documents
- `GET /api/ai/status` - Check AI classifier status

#### Example API Usage

```bash
# Classify a single document
curl -X POST http://localhost:5000/api/ai/classify \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "/path/to/document.pdf"}'

# Classify multiple documents
curl -X POST http://localhost:5000/api/ai/classify_batch \
  -H "Content-Type: application/json" \
  -d '{"pdf_paths": ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]}'

# Check AI status
curl http://localhost:5000/api/ai/status
```

## Model Setup

### Using Local Llama Model

1. **Download the model**:
   ```bash
   # Using HuggingFace CLI
   huggingface-cli download meta-llama/Llama-2-7b-chat-hf
   
   # Or using Python
   from transformers import AutoTokenizer, AutoModelForCausalLM
   model_name = "meta-llama/Llama-2-7b-chat-hf"
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   model = AutoModelForCausalLM.from_pretrained(model_name)
   ```

2. **Configure the model path** in `ai_config.json`:
   ```json
   {
       "model_config": {
           "model_name": "/path/to/local/llama-model",
           "device": "auto"
       }
   }
   ```

### Using Different Models

You can use different models by updating the configuration:

```json
{
    "model_config": {
        "model_name": "microsoft/DialoGPT-medium",
        "device": "cpu"
    }
}
```

## Performance

### Memory Requirements

- **Llama-2-7b**: ~14GB RAM (8-bit quantization: ~7GB)
- **CPU inference**: Slower but works on any machine
- **GPU inference**: Much faster, requires CUDA-compatible GPU

### Optimization Tips

1. **Use quantization** for lower memory usage:
   ```python
   model = AutoModelForCausalLM.from_pretrained(
       model_name,
       torch_dtype=torch.float16,
       device_map="auto",
       load_in_8bit=True  # For 8-bit quantization
   )
   ```

2. **Batch processing** for multiple documents
3. **Caching** model responses for repeated documents

## Testing

Run the test script to verify the classifier:

```bash
cd backend
python test_ai_classifier.py
```

## Troubleshooting

### Common Issues

1. **Model not loading**:
   - Check if model path is correct
   - Ensure sufficient memory (14GB+ for full model)
   - Try using CPU if GPU memory is insufficient

2. **AI dependencies not available**:
   - Install torch and transformers: `pip install torch transformers`
   - Check Python version compatibility

3. **Low confidence scores**:
   - Adjust confidence threshold in config
   - Review document content quality
   - Check if document is actually a financial report

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Pipeline

The AI classifier enhances the existing annual report discovery pipeline:

1. **Discovery phase**: Uses AI to validate candidate documents
2. **Download phase**: AI classification before saving documents
3. **Validation phase**: Confidence scores for quality assurance

### Benefits

- **Higher accuracy**: AI understands document context and structure
- **Reduced false positives**: Better filtering of non-annual reports
- **Improved coverage**: Finds more valid annual reports
- **Quality assurance**: Confidence scores for manual review

## Future Enhancements

1. **Model fine-tuning**: Fine-tune on financial documents
2. **Multi-language support**: Support for non-English documents
3. **Document structure analysis**: Analyze document layout and structure
4. **Learning from feedback**: Improve classification based on user feedback
5. **Real-time classification**: Stream processing for large document sets