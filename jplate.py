#!/home/hiryuu/Documents/tools/jplate/venv/bin/python
"""
TO-DO
- automatically download JMDict to project folder and unzip:
    -> wget into project folder https://github.com/scriptin/jmdict-simplified/releases/download/3.6.1%2B20250929122529/jmdict-eng-3.6.1+20250929122529.json.zip
    -> unzip *.zip && rm *.zip
- jmdict update check launch
- add option for expand
- show ID and add id lookup
- make settings/config file for api key and language settings -> download matching jmdict
- result lenght limit (...)


-chmod +x /home/hiryuu/Documents/tools/jplate/jplate.py
- sudo ln -s /home/hiryuu/Documents/tools/jplate/jplate.py /usr/local/bin/jplate
"""

import os
import json
import argparse
import jaconv
import deepl
from prompt_toolkit import PromptSession
from wcwidth import wcswidth


PATH = os.path.realpath(__file__)
DIR = os.path.dirname(PATH)
JMDICT = os.path.join(DIR, "jmdict-eng-3.6.1.json")
ZIP = os.path.join(DIR, "jmdict-eng-3.6.1+20250929122529.json.zip")
API_KEY_FILE = os.path.join(DIR, ".api_key.txt")


# ---------------------- CLI FORMATTING ---------------------- #
# ANSI color codes
ANSI_COLORS = {
    "INFO": "\033[94m",     # blue
    "ERROR": "\033[91m",    # red
    "RESULT": "\033[92m",   # green
    "KANA": "\033[92m",   # green
    "WARNING": "\033[93m",  # yellow/orange
    "HELP": "\033[96m",     # cyan
}
RESET = "\033[0m"
TAG_WIDTH = 9


def output(tag, text, return_str=False):
    color = ANSI_COLORS.get(tag.upper(), "")
    tag_str = f"[{tag.upper()}]".ljust(TAG_WIDTH)
    lines = text.splitlines()
    formatted_lines = [f"{color}{tag_str}{RESET}  -  {line}" for line in lines]
    s = "\n".join(formatted_lines)
    if return_str:
        return s
    print(s)

def display_width(text):
    return wcswidth(str(text))

# ---------------------- FUNCTIONS ---------------------- #
def lookup_jmdict(query, search_english=False, expand=False):
    results = []

    if not search_english:
        query_hira = jaconv.alphabet2kana(query)
        query_kata = jaconv.hira2kata(query_hira)

    with open(JMDICT, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.rstrip(",\n"))
            except json.JSONDecodeError:
                continue

            if search_english:
                # Search inside English glosses (exact match, case-insensitive)
                matched_senses = []
                for sense in entry.get("sense", []):
                    for gloss in sense.get("gloss", []):
                        if query.lower() == gloss.get("text", "").lower():
                            matched_senses.append(sense)
                            break
                if not matched_senses:
                    continue
            else:
                # Find kana that matches query
                matching_kana = [k for k in entry.get("kana", []) if k.get("text") in (query_hira, query_kata)]
                if not matching_kana:
                    continue

            # Filter common kanji only
            common_kanji = [k["text"] for k in entry.get("kanji", []) if k.get("common")]
            if not common_kanji:
                common_kanji = ["N/A"]  # fallback if no common kanji

            for kanji_text in common_kanji:
                gloss_text = "N/A"
                if search_english:
                    # Only consider the exact-match senses we collected
                    for sense in matched_senses:
                        partOfSpeech = sense.get("partOfSpeech", [])
                        for gloss in sense.get("gloss", []):
                            if query.lower() == gloss.get("text", "").lower():
                                if expand:
                                    gloss_text = "; ".join(
                                        g.get("text","N/A")
                                        for g in sense.get("gloss",[])
                                    )
                                else:
                                    gloss_text = gloss.get("text","N/A")
                                break
                        if gloss_text != "N/A":
                            break

                    if gloss_text == "N/A":
                        continue  # skip entries with no valid gloss

                    # Show all kana readings for English search
                    matching_kana = [k.get("text") for k in entry.get("kana", [])]
                    for kana_text in matching_kana:
                        results.append((partOfSpeech[0],kanji_text,kana_text,gloss_text))
                        
                # romaji lookup
                else:
                    #specific_gloss = None
                    #wildcard_gloss = None
                    specific_glosses = []
                    wildcard_glosses = []
                    query_hira = jaconv.alphabet2kana(query)

                    for sense in entry.get("sense", []):
                        partOfSpeech = sense.get("partOfSpeech", [])
                        applies = sense.get("appliesToKanji", ["*"])
                        glosses = sense.get("gloss", [])

                        if not glosses:
                            continue

                        texts = [g.get("text", "N/A") for g in glosses]

                        if kanji_text in applies:
                            specific_glosses.extend(texts)
                            if not expand:
                                break

                        elif "*" in applies:
                            wildcard_glosses.extend(texts)

                    # Decide gloss text
                    gloss_list = specific_glosses if specific_glosses else wildcard_glosses

                    if not gloss_list:
                        gloss_list = ["N/A"]

                    if expand:
                        gloss_text = "; ".join(gloss_list)
                    else:
                        gloss_text = gloss_list[0]            
                    for kana_elem in matching_kana:
                        results.append((partOfSpeech[0],kanji_text,kana_elem.get('text'),gloss_text))
    if results:
        num_cols = len(results[0]) if results else None
        col_widths = [
            max(display_width(row[i]) for row in results)
            for i in range(num_cols)
        ]
        pretty_results = []
        for row in results:
            parts = []
            for i, val in enumerate(row):
                text = str(val)
                pad = col_widths[i] - display_width(text)
                parts.append(text + " " * pad)
            pretty_results.append(" | ".join(parts))
        return pretty_results
    else:
        return None


def setup(API_KEY, ZIP, JMDICT):
    pass


# ---------------------- MAIN ---------------------- #
def main():
    parser = argparse.ArgumentParser(description="Japanese translation and dictionary CLI utility")
    parser.add_argument("input", nargs='?', help="Word to be looked up in the JMDict or sentence to be translated with DeepL")
    parser.add_argument("-x", "--expand", action="store_true", help="Also shows non-extact matches — negai would match onegai shimasu")
    parser.add_argument("-e", "--english", action="store_true", help="Searches for the english word instead")
    parser.add_argument("-d", "--deepl", action="store_true", help="Translates a Japanese string with DeepL - API key required")
    parser.add_argument("-de", "--deeplen", action="store_true", help="Translates a English string with DeepL - API key required")
    parser.add_argument("-v", "--verbose", action="store_true", help="Displays all available info for the queried word")
    parser.add_argument("-i", "--interactive", action="store_true", help="[WIP] Launch interactive input mode - default if no word is provided")
    args = parser.parse_args()


    query = args.input
    # DeepL translation mode
    if args.deepl:
        query_hira = jaconv.alphabet2kana(query)
        result = deepl_client.translate_text(f"{query}", target_lang="EN-US", source_lang='JA', model_type='prefer_quality_optimized')
        output("INFO", f"{query_hira}\n")
        output("RESULT", f"{result.text}\n")
    
    elif args.deeplen:
        result = deepl_client.translate_text(f"{query}", target_lang="JA", source_lang='EN', model_type='prefer_quality_optimized')
        output("RESULT", f"{result.text}\n")

    # JMDict single word dictionaty mode
    elif query is not None:
        if "," in args.input.strip():
            output("error", f"Dictionary lookup only supports a single word\nFor multiple words or sentences use interactive mode.")
        else:
            results = lookup_jmdict(query, search_english=args.english, expand=args.expand)
            if results is None:
                output("WARNING", "No results found")
            else:
                for result in results:
                    output("RESULT", f"{result}\n")
    
    # Interactive mode — not yet implemented
    else:
        quit()
        session = PromptSession(f"JPlate   >>>  ")
        output("info", f"Using Interactive mode — Type 'help' for help")
        while True:
            try:
                text = session.prompt()
                if text == "help":
                    output("help", "Single word > JMDict lookup\nMultiple words > DeepL translation\nCtrl+d to exit")
                else:
                    output("result", text)
                    #print(process(text))
            except KeyboardInterrupt:
                continue
            except EOFError:
                break


if __name__ == "__main__":
    try:
        with open(API_KEY_FILE) as f:
            api_key = f.read()
            deepl_client = deepl.DeepLClient(api_key)
    except FileNotFoundError:
        output("warning", "No API key found — DeepL translation unsupported")
        deepl_client = None
        pass

    main()
