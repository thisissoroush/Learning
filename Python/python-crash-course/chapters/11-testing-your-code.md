# Chapter 11 — Testing Your Code

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Writing tests with pytest, assertions, fixtures, testing functions and classes.

---

## 🧪 Testing a Function

```python
# name_function.py
def get_formatted_name(first, last, middle=''):
    """Generate a neatly formatted full name."""
    if middle:
        full_name = f"{first} {middle} {last}"
    else:
        full_name = f"{first} {last}"
    return full_name.title()
```

```python
# test_name_function.py
from name_function import get_formatted_name

def test_first_last_name():
    """Do names like 'Janis Joplin' work?"""
    formatted_name = get_formatted_name('janis', 'joplin')
    assert formatted_name == 'Janis Joplin'

def test_first_last_middle_name():
    """Do names like 'Wolfgang Amadeus Mozart' work?"""
    formatted_name = get_formatted_name('wolfgang', 'mozart', 'amadeus')
    assert formatted_name == 'Wolfgang Amadeus Mozart'
```

```bash
# Run pytest
pytest
# ============================= test session starts ==============================
# collected 2 items
# test_name_function.py ..                                              [100%]
# ============================== 2 passed in 0.01s ===============================

# Verbose output
pytest -v
```

---

## ✅ Assertions

```python
# Common assertions in pytest
assert value == expected
assert value != expected
assert value > 0
assert value is None
assert 'substring' in string
assert item in list
assert item not in list

# pytest shows detailed info on failure:
# AssertionError: assert 'Wolfgang Mozart' == 'Wolfgang Amadeus Mozart'
```

---

## 🔴 A Failing Test

```python
# If we change get_formatted_name to require middle name:
def get_formatted_name(first, middle, last):
    ...

# test_first_last_name now FAILS:
# FAILED test_name_function.py::test_first_last_name - TypeError

# Failed test output:
# FAILED test_name_function.py::test_first_last_name
# ========================= 1 failed, 1 passed in 0.02s =========================

# Fix the function, not the test!
# Tests reveal bugs — don't delete them when they fail
```

---

## 🏛️ Testing a Class

```python
# survey.py
class AnonymousSurvey:
    """Collect anonymous answers to a survey question."""

    def __init__(self, question):
        self.question = question
        self.responses = []

    def show_question(self):
        print(self.question)

    def store_response(self, new_response):
        self.responses.append(new_response)

    def show_results(self):
        print("Survey results:")
        for response in self.responses:
            print(f"- {response}")
```

```python
# test_survey.py
import pytest
from survey import AnonymousSurvey

# Fixture — shared setup across multiple tests
@pytest.fixture
def language_survey():
    """An AnonymousSurvey that will be available to all test functions."""
    question = "What language did you first learn to speak?"
    language_survey = AnonymousSurvey(question)
    return language_survey

def test_store_single_response(language_survey):
    """Test that a single response is stored properly."""
    language_survey.store_response('English')
    assert 'English' in language_survey.responses

def test_store_three_responses(language_survey):
    """Test that three individual responses are stored properly."""
    responses = ['English', 'Spanish', 'Mandarin']
    for response in responses:
        language_survey.store_response(response)
    for response in responses:
        assert response in language_survey.responses
```

---

## 📋 Full pytest Assertions Table

```python
# Value equality
assert result == 42
assert result != 0

# Comparisons
assert result > 0
assert result <= 100

# Truthiness
assert result          # truthy
assert not result      # falsy

# None checks
assert result is None
assert result is not None

# Membership
assert 'key' in my_dict
assert item in my_list
assert value not in my_set

# Type check
assert isinstance(result, int)
assert isinstance(result, (list, tuple))

# Exception testing
with pytest.raises(ValueError):
    int("not a number")
```

---

## 🔑 Key Takeaways

- pytest discovers test files named `test_*.py` and test functions named `test_*`
- Each test function tests ONE specific behavior
- `assert` verifies the expected result — pytest shows detailed failure info
- When a test fails: fix the **code**, not the test (unless the test itself is wrong)
- `@pytest.fixture` creates shared setup objects — eliminates duplicate setup code
- Fixtures are passed as parameters to test functions (pytest injects them)
- Write tests for the common case, the edge cases, and the expected failures
