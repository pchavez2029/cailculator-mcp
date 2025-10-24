# Day 1 Build Checklist - MCP Server Core

**Goal**: Working MCP server that responds to tool calls

---

## Morning Session (3-4 hours)

### 1. Implement server.py ⏱️ 90 min
- [ ] Copy MCP server template from plan
- [ ] Set up MCP Server instance
- [ ] Implement `list_tools()` handler
- [ ] Implement `call_tool()` handler with auth check
- [ ] Add main() and run() functions
- [ ] Test server starts: `cailculator-mcp`

### 2. Implement tools.py ⏱️ 90 min
- [ ] Define TOOLS_DEFINITIONS array (3 tools)
- [ ] Implement `chavez_transform()` async function
  - Parse input data
  - Call ChavezTransform from transforms.py
  - Format JSON response
- [ ] Implement `detect_patterns()` stub (basic version)
- [ ] Implement `analyze_dataset()` (combines transform + patterns)
- [ ] Add helper functions for formatting

---

## Afternoon Session (2-3 hours)

### 3. Create patterns.py ⏱️ 60 min
- [ ] Create Pattern dataclass
- [ ] Create PatternDetector class
- [ ] Implement `_detect_conjugation_symmetry()`
- [ ] Implement `_detect_bilateral_zeros()` (simple version)
- [ ] Implement `_detect_dimensional_persistence()`

### 4. Testing & Debugging ⏱️ 90 min
- [ ] Set up dev environment: `pip install -e ".[dev]"`
- [ ] Set dev API key: `CAILCULATOR_API_KEY=dev_test`
- [ ] Set dev mode: `CAILCULATOR_ENABLE_DEV_MODE=true`
- [ ] Test server starts without errors
- [ ] Test with simple data array
- [ ] Fix any bugs

---

## Evening Session (1 hour)

### 5. Documentation & Cleanup ⏱️ 60 min
- [ ] Add docstrings to main functions
- [ ] Update README if needed
- [ ] Create simple test data file for tomorrow
- [ ] Document any issues encountered
- [ ] Plan Day 2 (auth server)

---

## Testing Checklist

Run these tests before calling it a day:

```bash
# 1. Server starts
cailculator-mcp

# 2. No import errors
python -c "from cailculator_mcp.server import app; print('OK')"

# 3. Tools defined
python -c "from cailculator_mcp.tools import TOOLS_DEFINITIONS; print(len(TOOLS_DEFINITIONS))"

# 4. Transform works
python -c "from cailculator_mcp.transforms import ChavezTransform; print('OK')"
```

---

## Done When...

✅ Server starts without errors
✅ Three tools defined and callable
✅ Dev API key authentication works
✅ Basic transform runs successfully
✅ Ready to integrate with auth server tomorrow

---

## If You Get Stuck

- Reference: MCP-CAILculator/MCP Plan for CAILculator10_21_2025.txt (lines 190-679)
- MCP docs: https://modelcontextprotocol.io/docs
- Test incrementally (don't wait until everything is done)

---

**Remember**: MVP first, polish later. Get it working, then make it pretty.

**Chavez AI Labs**
