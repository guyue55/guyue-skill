# Feishu Publishing

## 1. Publication States

Report these states separately:

| State | Meaning |
| --- | --- |
| `local_ready` | Local document and deck pass their checks |
| `doc_published` | Online Docx was created or overwritten and fetched back |
| `ppt_file_uploaded` | Portable HTML exists in the target Drive folder |
| `uploaded_not_render_verified` | HTML is stored, but browser execution was not proven |
| `online_preview_verified` | The actual Feishu/browser page rendered slides and navigation successfully |
| `blocked` | Authorization, access, scope, conflict, or preview verification failed |

Never map `ppt_file_uploaded` to `online_preview_verified` without a browser check.

## 2. Read Version-Matched CLI Guidance

Before using `lark-cli`, read:

```bash
lark-cli skills read lark-shared SKILL.md
lark-cli skills read lark-doc
lark-cli skills read lark-drive
```

Then read only the references required by the chosen commands, especially document update/fetch/media insertion and Drive list/upload/push/status.

Use `--as user` for a user's Drive folder. Verify with:

```bash
lark-cli auth status --json --verify
```

If authorization is missing, use the split device flow described by `lark-shared`. Do not expose or store tokens.

## 3. Resolve The Target

Extract the folder token from the user URL and list the direct children:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder-token>","page_size":200}' \
  --as user --format json
```

Match both title and type. Do not overwrite a same-name Sheet, file, or unrelated Docx. If multiple same-name Docx files exist, stop and ask which token to preserve.

## 4. Prepare The Document

Run from the project root so local image paths remain usable by `lark-cli`:

```bash
python3 <skill-root>/scripts/prepare_feishu_publish.py \
  --source docs/share/<topic>/<topic>-方案.md \
  --output-dir tmp/feishu-publish
```

Outputs:

- `document.md`: local image lines removed; other content preserved.
- `media-plan.json`: image path, insertion text, position, and display size.

Review warnings about unresolved images, duplicate insertion text, or local-only links before writing.

## 5. Overwrite Or Create The Docx

When a matching Docx exists and overwrite is approved:

```bash
lark-cli docs +update \
  --doc <doc-token> \
  --command overwrite \
  --content @tmp/feishu-publish/document.md \
  --doc-format markdown \
  --as user --format json
```

When none exists, use `docs +create` with the target folder token and the prepared Markdown. Preserve the returned document ID.

Insert media sequentially. The current `docs +media-insert` shortcut appends media; it does not accept a text selection or before/after flag. For each `media-plan.json` entry:

```bash
lark-cli docs +media-insert \
  --doc <doc-token> \
  --file <relative-image-path> \
  --align center \
  --width <display-width> \
  --height <display-height> \
  --as user --format json
```

Then:

1. fetch the relevant section with `--detail with-ids`;
2. identify the new image block and the recorded text anchor;
3. use `docs +update --command block_move_after` to move the image;
4. for `position=after`, use the anchor block as `--block-id`;
5. for `position=before`, use the anchor block's preceding sibling as `--block-id`;
6. fetch the section again before placing the next image because block positions changed.

Do not leave all images at the document end. If the anchor is ambiguous, stop rather than guessing.

## 6. Upload The Portable PPT

The portable PPT must be a genuine single file before upload. Read the current `lark-drive` upload reference before choosing flags; CLI behavior may change.

Create a new file only when no same-name HTML exists:

```bash
lark-cli drive +upload \
  --file <share-root>/ppt/index-feishu.html \
  --folder-token <folder-token> \
  --name index-feishu.html \
  --as user --format json
```

When a same-name HTML exists and overwrite is approved, preserve its token:

```bash
lark-cli drive +upload \
  --file <share-root>/ppt/index-feishu.html \
  --file-token <existing-file-token> \
  --as user --format json
```

After upload:

1. re-list the target folder;
2. confirm the file name, type, token, and modified time;
3. compare local/remote status or download hash when the CLI supports it;
4. open the actual Feishu URL in a browser if online rendering is part of the promise.

If Feishu stores or downloads the HTML but does not execute it, report `uploaded_not_render_verified`. Offer a separately authorized static-hosting route only when the user needs a browser-executable URL; do not silently publish outside Feishu.

## 7. Online Verification

Fetch the Docx after all insertions:

```bash
lark-cli docs +fetch \
  --doc <doc-token> \
  --detail simple \
  --as user --format json
```

Verify:

- title and final section exist;
- image count equals the media plan;
- generated Mermaid/whiteboard count is expected;
- no local image syntax or local file link remains;
- no Markdown alert marker such as `[!NOTE]` is visibly left behind;
- the folder still contains one intended Docx and one intended HTML file.

Return both URLs and the publication states. A command response with `ok: true` proves that operation only, not the whole publication.
