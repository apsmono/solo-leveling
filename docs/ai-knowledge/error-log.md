# Error Log

Documented errors encountered during development, with root cause, fix, and prevention rule.
Add new entries at the top of the list.

---

## 2026-04-17 — `__init__.py` content written to wrong file

**Symptom:** `src/integrations/notion/__init__.py` contained `.env.example` content instead of being empty.

**Root cause:** A multi-step file creation block mixed empty-file creation with content-bearing file creation; the wrong content was passed to the wrong `create_file` call.

**Fix:** Used `replace_string_in_file` to replace the wrong content with an empty string immediately after detecting the error.

**Prevention rule:** When creating a batch of `__init__.py` files, always use `create_file` with empty content (`""`) and verify each one before moving on. Do not mix empty-file creation with content-bearing file creation in the same block.

---

## 2026-04-17 — `multi_replace_string_in_file` partial failure on CHANGELOG

**Symptom:** One of three replacements in a `multi_replace_string_in_file` call returned a "string not found" error even though the content existed before the call.

**Root cause:** An earlier replacement in the same call inserted a new line above the target string, which shifted enough context that the second match string no longer exactly matched the file's current state at the time of the second replacement.

**Fix:** Read the file after the partial failure to see the actual current content, then made the remaining replacement individually using `replace_string_in_file` with fresh context lines.

**Prevention rule:** In `multi_replace_string_in_file`, if two replacements target nearby lines in the same file, make them sequential (separate calls) rather than parallel. Only batch replacements that are in different files or in clearly non-overlapping sections of the same file.

---

## 2026-04-17 — `apply_patch *** Add File:` on an already-existing file

**Symptom:** `apply_patch` silently failed or produced a conflict when used to "create" a file that already existed.

**Root cause:** `apply_patch *** Add File:` is intended for genuinely new files only. Using it on an existing file produces undefined behaviour.

**Fix:** Use `read_file` first to confirm whether a file exists. If it does, use `replace_string_in_file` or `multi_replace_string_in_file` to edit it. Only use `create_file` for files confirmed to be absent.

**Prevention rule:** Before creating any file, verify it does not already exist with `list_dir` or `file_search`. If it exists, edit — never recreate.
