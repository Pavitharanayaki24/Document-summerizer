# Upload flow: changes in `frontend/src/App.jsx` and `backend/app.py`

This document describes what changed in these two files and **why**, so you can keep or restore the behavior without guessing.

---

## `frontend/src/App.jsx`

### 1. Do not set `Content-Type` manually on multipart uploads

**Change:** `POST /upload` sends `FormData` with `axios.post(url, formData)` and **no** `headers: { "Content-Type": "multipart/form-data" }`.

**Why:** Multipart requests must include a **boundary** in the header (e.g. `multipart/form-data; boundary=----WebKitFormBoundary...`). If you set only `multipart/form-data`, the boundary is missing. The browser cannot parse the body correctly; Flask often sees **no file** (`request.files` empty), which leads to failed or flaky uploads.

Letting axios (or the browser) set `Content-Type` automatically includes the correct boundary.

### 2. Show server error messages on upload failure

**Change:** In the `catch` block for upload, the UI prefers `error.response?.data?.error` from the JSON body, with a fallback for generic failures.

**Why:** The backend returns structured errors (e.g. “no extractable text”, validation messages). Surfacing `error` in the UI helps you see **what** failed instead of only “Upload failed.”

---

## `backend/app.py`

### 1. `werkzeug.utils.secure_filename` and temp path under `BACKEND_DIR`

**Change:** The uploaded file is saved as `os.path.join(BACKEND_DIR, f"temp_{safe_name}")` where `safe_name = secure_filename(file.filename)`.

**Why:**

- Filenames from the client can contain unsafe characters or path segments; `secure_filename` reduces path issues on Windows and in general.
- Saving next to the app with a known base directory avoids surprises when the process working directory differs.

### 2. Absolute `VECTOR_STORE_PATH`

**Change:** `VECTOR_STORE_PATH = os.path.join(BACKEND_DIR, "Fetching", "vector_store")` instead of a relative `"Fetching/vector_store"`.

**Why:** Relative paths depend on **current working directory** when you start Flask. If you run from another folder, the index could be written somewhere unexpected while `Fetching/query.py` still loads from `Fetching/vector_store` next to its package. One absolute path keeps **save** and **load** aligned.

### 3. Single import of `ask_question`

**Change:** Removed duplicate `from Fetching.query import ask_question`.

**Why:** Duplicate imports are redundant and can confuse readers or tooling.

### 4. Guard: no extractable text before embedding

**Change:** After `load_document`, the code checks that at least one document has non-empty `page_content`. For PDFs with no text, it returns **400** with a clear message (scanned/image-only PDF case). If chunking yields no chunks, it returns **400** with another message.

**Why:** Image-only or empty-extraction PDFs used to fail later (e.g. embedding / FAISS with empty input), often as a **500** with a cryptic error like `list index out of range`. Failing fast with **400** and a readable message is easier to understand and matches “bad input,” not “server bug.”

### 5. `finally`: always remove the temp file

**Change:** Temp file deletion runs in `finally` if `temp_path` exists.

**Why:** If an exception happens after `file.save` (e.g. during load or embedding), the old code might not remove the temp file. `finally` keeps the backend directory from filling with `temp_*` leftovers.

---

## Summary

| Area | What | Why |
|------|------|-----|
| Frontend | No manual multipart `Content-Type` | Correct boundary so Flask receives the file reliably |
| Frontend | Use API `error` in UI when present | Clear feedback from the server |
| Backend | `secure_filename` + path under `BACKEND_DIR` | Safer, predictable temp file location |
| Backend | Absolute vector store path | Save and load FAISS index to the same place regardless of cwd |
| Backend | Dedupe `ask_question` import | Cleaner module |
| Backend | Empty text / empty chunks → 400 | Avoid 500s on unscannable PDFs; explain the issue |
| Backend | `finally` deletes temp file | Cleanup on success and on error |
