# Structured Description Modification Summary

## Overview
Modified the `describe_image` method in `src/processors/llm_agent.py` to return structured JSON output with specific keys: `text`, `description`, `scene`, and `context`.

## Files Modified

### 1. `config/llm_schema.yml`
**Changes Made:**
- Updated the `description_schema` to define the new structured format
- Changed required fields from just `description` to include all four keys: `text`, `description`, `scene`, `context`

**New Schema:**
```yaml
description_schema:
  type: object
  properties:
    text:
      type: string
      description: Any readable text found in the image
    description:
      type: string
      description: Detailed description of the image content
    scene:
      type: string
      description: Overall scene or setting of the image
    context:
      type: string
      description: Context or situation depicted in the image
  required:
    - text
    - description
    - scene
    - context
```

### 2. `src/processors/llm_agent.py`
**Changes Made:**
- Added `_validate_description_schema()` helper method for data validation
- Completely rewrote `describe_image()` method to:
  - Use structured JSON prompt with explicit schema
  - Request JSON format from Ollama using `'format': 'json'`
  - Parse and validate JSON response
  - Return structured data with all four required keys
  - Include robust error handling and fallback mechanisms

**New Method Features:**
- Structured prompt that explicitly requests JSON format
- JSON parsing with error handling
- Data validation and normalization
- Raw response included in return for debugging
- Comprehensive logging

### 3. `src/models/image_data.py`
**Changes Made:**
- Extended `ImageData` model to include new structured description fields:
  - `description_text`: Text found in image
  - `description_scene`: Scene description
  - `description_context`: Context description
- Maintained backward compatibility with existing `description` field

### 4. `src/processors/processor.py`
**Changes Made:**
- Updated the image processing workflow to handle structured description response
- Extract all four structured fields from LLM response
- Enhanced logging to show scene, context, and found text
- Pass structured data to `ImageData` constructor

**New Processing Flow:**
```python
# Extract structured description data
description = description_result.get('description', '')
description_text = description_result.get('text', '')
description_scene = description_result.get('scene', '')
description_context = description_result.get('context', '')
```

### 5. `test_structured_description.py` (New File)
**Purpose:**
- Test script to validate the structured description functionality
- Checks Ollama connection
- Tests with actual image files
- Displays structured output in readable format
- Shows raw JSON response for debugging

## Key Features Implemented

### 1. **Structured JSON Response**
The LLM now returns responses in this exact format:
```json
{
    "text": "Any readable text found in the image",
    "description": "Detailed description of image content",
    "scene": "Overall scene or setting",
    "context": "Context or situation depicted"
}
```

### 2. **Robust Error Handling**
- JSON parsing errors are caught and handled gracefully
- Fallback to previous behavior if structured parsing fails
- Validation ensures all required keys are present
- Raw response preserved for debugging

### 3. **Data Validation**
- `_validate_description_schema()` ensures data consistency
- Handles None values and type conversions
- Normalizes string data (strips whitespace)

### 4. **Backward Compatibility**
- Existing `description` field maintained in `ImageData`
- Processor continues to work with legacy code
- Additional structured fields are optional enhancements

### 5. **Enhanced Logging**
- Detailed logging of structured data extraction
- Shows character counts and preview of content
- Logs found text separately when present

## Usage Example

```python
from src.processors.llm_agent import LLMAgent

agent = LLMAgent('qwen3-vl:4b')
result = agent.describe_image('path/to/image.jpg')

if result['success']:
    print(f"Text found: {result['text']}")
    print(f"Description: {result['description']}")
    print(f"Scene: {result['scene']}")
    print(f"Context: {result['context']}")
```

## Benefits

1. **Structured Data**: Clear separation of different types of information
2. **Better Analytics**: Can analyze scene types, contexts, and text separately
3. **Improved Processing**: Downstream systems can use specific data fields
4. **Debugging**: Raw JSON response preserved for troubleshooting
5. **Flexibility**: Schema can be extended for future requirements

## Testing

Run the test script to verify functionality:
```bash
python test_structured_description.py
```

This will test the complete pipeline and display structured results.

## Compatibility Notes

- Requires Ollama with a vision-capable model (e.g., qwen3-vl:4b)
- Uses `'format': 'json'` parameter which requires recent Ollama versions
- Backward compatible with existing code that uses `description` field
- All structured fields default to empty strings if not provided by LLM