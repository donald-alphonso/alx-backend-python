# Unittests and Integration Tests

This project contains unit and integration tests for utility functions written in Python.

## 📚 Purpose

The goal is to understand and practice:

- The difference between **unit tests** and **integration tests**
- Writing **parameterized tests**
- Using **mocking** with `unittest.mock`
- Test-driven development principles

## 🧪 What's Tested?

### ✅ `access_nested_map`

We test the `access_nested_map` function with various inputs using **parameterized unit tests**.

Example:

```python
access_nested_map({"a": {"b": 2}}, ("a", "b"))  # returns 2
```
