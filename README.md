# jplate

A command-line Japanese dictionary and translation tool built on [JMdict](https://github.com/scriptin/jmdict-simplified) and [DeepL](https://www.deepl.com/en/products/api).

## Requirements

- Python 3.x
- JMdict JSON dictionary file (see [Dictionary Setup](#dictionary-setup))
- DeepL API key (optional — only needed for translation features)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/f0xg0d/jplate.git
   cd jplate
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Add your DeepL API key:
   ```bash
   echo "your_api_key_here" > .api_key.txt
   ```

5. (Optional) Make it available system-wide:
   ```bash
   chmod +x jplate.py
   sudo ln -s "$(pwd)/jplate.py" /usr/local/bin/jplate
   ```

## Dictionary Setup

The JMdict file is not included in this repository due to its size. Download the English JSON release from:

**[jmdict-simplified releases](https://github.com/scriptin/jmdict-simplified/releases)**

Download the `jmdict-eng-*.json.zip` file, unzip it, and place the `.json` file in the project root.

```bash
wget https://github.com/scriptin/jmdict-simplified/releases/download/3.6.2%2B20260316124936/jmdict-eng-3.6.2+20260316124936.json.zip
unzip *.zip && rm *.zip
```

## Usage

```
jplate [OPTIONS] [WORD]
```

### Options

| Flag | Description |
|------|-------------|
| `-e, --english` | Search by English word instead of Japanese/romaji |
| `-x, --expand` | Show expanded results including non-exact matches |
| `-d, --deepl` | Translate Japanese → English using DeepL (API key required) |
| `-de, --deeplen` | Translate English → Japanese using DeepL (API key required) |
| `-v, --verbose` | Display all available info for the queried word |
| `-i, --interactive` | ⚠️ Launch interactive input mode (WIP — not yet implemented) |

### Examples

```bash
# Look up a Japanese word by romaji
jplate taberu
[RESULT]   -  int | N/A | ありがとう | thank you

# Look up using kana
jplate たべる
[RESULT]   -  v1 | 食べる | たべる | to eat

# Search by English definition
jplate -e 'to eat'
[RESULT]   -  v1    | 食べる     | たべる       | to eat

# Show expanded matches
jplate -x daijoubu
[RESULT]   -  n | 大丈夫 | だいじょうぶ | safe; secure; sound; problem-free; without fear; all right; alright; OK; okay; certainly; surely; undoubtedly; no thanks; I'm good; that's alright; great man; fine figure of a man

# Translate Japanese to English (requires DeepL API key)
jplate -d "今日はいい天気ですね"
[INFO]     -  今日はいい天気ですね
[RESULT]   -  It's a nice day today, isn't it?

# Translate English to Japanese
jplate -de "The weather is nice today"
[RESULT]   -  今日は天気がいいです
```

## License

This project is released under the MIT License.

The JMdict dictionary is the property of the Electronic Dictionary Research and Development Group, used in accordance with their [licence](https://www.edrdg.org/edrdg/licence.html).
