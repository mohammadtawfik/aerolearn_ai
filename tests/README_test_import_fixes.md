# Ensuring Correct `Course` Model Usage in Integration Tests

**Problem:**  
Some errors (e.g. `'title' is an invalid keyword argument for Course'`) occur because a UI or non-ORM `Course` class is imported instead of the ORM SQLAlchemy class.

## Solution Steps

1. **Always import from the models module:**
   ```python
   from app.models.course import Course
   ```

2. **Do not import `Course` from UI, service, or script modules in _any_ test file or test fixture.**
   - Double check that your `conftest.py` and test modules have the correct import paths.

3. **If unsure:**  
   Add a debug print in your test just before using `Course`:
   ```python
   print("Course type used in test:", Course, Course.__module__)
   ```
   It should print: `app.models.course`.

4. **Update your IDE/project settings, if needed**, to prioritize model code over script/UI code.

---

_This will prevent future issues with param initialization and mapping errors._