import os
import sys

# --- Configuration ---
# 1. Path is set to the current directory (".").
WEBSITE_FOLDER = "."

# 2. Set the names of your link files
ORIGINAL_LINKS_FILE = "links.txt"
REDIRECT_LINKS_FILE = "redirects.txt"

# 3. Get the name of this script to avoid processing it
#    (We get the absolute path to be safe)
try:
    THIS_SCRIPT_NAME = os.path.abspath(__file__)
except NameError:
    # Fallback if running in an environment where __file__ isn't defined
    THIS_SCRIPT_NAME = os.path.abspath(sys.argv[0])

# Get absolute paths for the link files as well
ORIG_LINKS_PATH = os.path.abspath(ORIGINAL_LINKS_FILE)
REDI_LINKS_PATH = os.path.abspath(REDIRECT_LINKS_FILE)

# --- Files and directories to explicitly skip ---
# We use absolute paths to ensure we skip them even if
# os.walk provides a relative path like './script.py'
FILES_TO_SKIP = {THIS_SCRIPT_NAME, ORIG_LINKS_PATH, REDI_LINKS_PATH}
DIRS_TO_SKIP = {".git", ".svn", "node_modules", "__pycache__"}
# -----------------------------------------------


def load_links_from_file(filepath):
    """Reads all lines from a file, stripping whitespace."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # Read all lines, strip whitespace, and filter out any empty lines
            links = [line.strip() for line in f if line.strip()]
            return links
    except FileNotFoundError:
        print(f"❌ FATAL ERROR: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not read {filepath}: {e}")
        return None


def main():
    print("--- Starting Recursive Link Replacement ---")

    # --- 1. Load Original and New Links ---
    original_links = load_links_from_file(ORIGINAL_LINKS_FILE)
    new_links = load_links_from_file(REDIRECT_LINKS_FILE)

    if original_links is None or new_links is None:
        print("One or more link files could not be read. Exiting.")
        sys.exit(1)

    print(f"Loaded {len(original_links)} links from '{ORIGINAL_LINKS_FILE}'")
    print(f"Loaded {len(new_links)} links from '{REDIRECT_LINKS_FILE}'")

    # --- 2. Safety Check and Create Replacement Map ---
    if len(original_links) != len(new_links):
        print("\n" + "!" * 60)
        print("  WARNING: FILE MISMATCH!")
        print(f"  '{ORIGINAL_LINKS_FILE}' has {len(original_links)} lines.")
        print(f"  '{REDIRECT_LINKS_FILE}' has {len(new_links)} lines.")
        print("  This means your links are NOT 1-to-1.")
        print("  Continuing will cause INCORRECT REPLACEMENTS.")
        print("!" * 60 + "\n")

        try:
            # Force user to confirm they understand the risk
            confirm = input(
                f"Type 'CONTINUE' to proceed with the first {min(len(original_links), len(new_links))} pairs: "
            )
            if confirm != "CONTINUE":
                print("Aborted by user.")
                sys.exit(0)
        except EOFError:
            print("Aborting due to file mismatch in non-interactive mode.")
            sys.exit(1)

    link_map = dict(zip(original_links, new_links))

    if not link_map:
        print("Link files are empty. Nothing to replace. Exiting.")
        sys.exit(0)

    print(f"\nCreated replacement map with {len(link_map)} pairs.")
    print(f"Scanning folder: {os.path.abspath(WEBSITE_FOLDER)}\n")

    # --- 4. Walk and Replace ---
    total_files_scanned = 0
    total_files_changed = 0
    total_replacements_made = 0

    for root, dirs, files in os.walk(WEBSITE_FOLDER, topdown=True):
        # Skip common "binary" or "source control" directories
        dirs[:] = [d for d in dirs if d not in DIRS_TO_SKIP]

        for filename in files:
            file_path = os.path.join(root, filename)
            abs_file_path = os.path.abspath(file_path)

            # *** MODIFICATION ***
            # Skip this script, links.txt, and redirects.txt
            if abs_file_path in FILES_TO_SKIP:
                print(f"ℹ️ Skipping (source file): {file_path}")
                continue

            # *** REMOVED THE FILE EXTENSION CHECK ***

            total_files_scanned += 1
            file_was_changed = False

            try:
                # Read the file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            except UnicodeDecodeError:
                # This is crucial: it skips binary files (images, etc.)
                print(f"ℹ️ Skipping (binary file?): {file_path}")
                continue
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                continue

            # Perform the replacements
            new_content = content
            for original_link, new_link in link_map.items():
                if original_link in new_content:
                    # Count occurrences before replacing
                    count = new_content.count(original_link)
                    # Replace all occurrences
                    new_content = new_content.replace(original_link, new_link)

                    total_replacements_made += count
                    file_was_changed = True

            # Write the file back *only* if it was changed
            if file_was_changed:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"✅ Replaced links in: {file_path}")
                    total_files_changed += 1
                except Exception as e:
                    print(f"❌ Error writing changes to {file_path}: {e}")

    # --- 5. Final Report ---
    print("\n" + "=" * 30)
    print("Replacement complete.")
    print(f"Total files scanned: {total_files_scanned}")
    print(f"Total files modified: {total_files_changed}")
    print(f"Total replacements made: {total_replacements_made}")
    print("=" * 30)


if __name__ == "__main__":
    main()
