"""
Scan a Facebook data export for message JSON files and report any fields
that aren't in the "expected" schema, so you can decide how to handle them
before loading into SQL.

Usage:
    python scan_fb_fields.py /path/to/facebook_export_root
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# --- Known/expected fields, updated with what scan #1 found ---
EXPECTED_TOP_LEVEL = {
    "participants", "messages", "title", "is_still_participant",
    "thread_path", "magic_words",
    "image", "is_pending", "joinable_mode",
}
EXPECTED_PARTICIPANT = {"name"}
EXPECTED_MESSAGE = {
    "sender_name", "timestamp_ms", "content", "is_geoblocked_for_viewer",
    "audio_files", "bumped_message_metadata", "call_duration", "files",
    "gifs", "ip", "is_unsent", "missed", "photos", "reactions", "share",
    "sticker", "videos",
}

# Folders that typically contain message json (per your screenshot)
MESSAGE_FOLDERS = {"archived_threads", "filtered_threads", "inbox", "message_requests"}

# Inside each individual thread folder (e.g. inbox/260608097764728), we expect
# only these subfolders plus message_*.json files.
EXPECTED_THREAD_SUBFOLDERS = {"audio", "gifs", "photos", "videos"}


def scan_file(path, unexpected):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        unexpected["__FILES_FAILED_TO_PARSE__"].add(f"{path} ({e})")
        return

    if not isinstance(data, dict):
        unexpected["__NON_DICT_ROOT__"].add(str(path))
        return

    # top-level
    for key in data.keys():
        if key not in EXPECTED_TOP_LEVEL:
            unexpected["top_level"].add(key)

    # participants
    for p in data.get("participants", []) or []:
        if isinstance(p, dict):
            for key in p.keys():
                if key not in EXPECTED_PARTICIPANT:
                    unexpected["participant"].add(key)

    # messages
    for m in data.get("messages", []) or []:
        if isinstance(m, dict):
            for key in m.keys():
                if key not in EXPECTED_MESSAGE:
                    unexpected["message"].add(key)


def scan_folder_structure(root, unexpected):
    for container in MESSAGE_FOLDERS:
        container_path = root / container
        if not container_path.is_dir():
            continue

        for thread_dir in container_path.iterdir():
            if not thread_dir.is_dir():
                # unexpected file directly under archived_threads/inbox/etc
                unexpected["unexpected_item_in_container"].add(
                    f"{container}/{thread_dir.name}"
                )
                continue

            for item in thread_dir.iterdir():
                if item.is_dir():
                    if item.name not in EXPECTED_THREAD_SUBFOLDERS:
                        unexpected["unexpected_thread_subfolder"].add(item.name)
                elif item.is_file():
                    if item.suffix == ".json":
                        if not item.name.startswith("message_"):
                            unexpected["unexpected_json_filename"].add(item.name)
                    else:
                        unexpected["unexpected_file_in_thread_root"].add(item.name)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_fb_fields.py /path/to/facebook_export_root")
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.exists():
        print(f"Path does not exist: {root}")
        sys.exit(1)

    unexpected = defaultdict(set)
    files_scanned = 0

    for json_path in root.rglob("*.json"):
        # only look inside the message-container folders, skip things like
        # autofill_information.json, messenger_contacts_you've_blocked.json, etc.
        if not any(part in MESSAGE_FOLDERS for part in json_path.parts):
            continue
        # message json files are usually named message_1.json, message_2.json...
        if not json_path.name.startswith("message_"):
            continue

        files_scanned += 1
        scan_file(json_path, unexpected)

    scan_folder_structure(root, unexpected)

    print(f"Scanned {files_scanned} message json files under {root}\n")

    if not unexpected:
        print("No unexpected fields found. Your schema assumption holds.")
        return

    for category, keys in unexpected.items():
        print(f"[{category}]")
        for k in sorted(keys):
            print(f"  - {k}")
        print()


if __name__ == "__main__":
    main()