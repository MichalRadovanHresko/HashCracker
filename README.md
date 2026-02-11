# HashCracker

A cross-platform SHA-256 password brute-force tool with GUI support for salted hashes commonly used in systems like AuthMe Minecraft plugins.

**Status**: **Python**: 3.8+ | **License**: Educational

## DISCLAIMER

**This tool is for educational and authorized security testing purposes only.**

- Use this tool **ONLY** on systems you own or have explicit written permission to test
- Unauthorized password cracking is **ILLEGAL**
- The author is **NOT RESPONSIBLE** for any illegal use or damage caused
- Violating these terms may result in criminal prosecution

## How to use it 

### For Regular Users
1. Go to [Releases](https://github.com/MichalRadovanHresko/HashCracker/releases)
2. Download: `HashCracker.app` (macOS), `HashCracker.exe` (Windows), or `HashCracker` (Linux)
3. Double-click and run

Done! No Python or installation needed.

## Features

- **SHA-256 Brute Force** - Tests password combinations against hashes
- **Salted Hash Support** - Works with `SHA256(SHA256(password) + salt)` format (AuthMe)
- **Custom Charsets** - Choose: a-z, A-Z, 0-9, All, Letters, Alphanumeric
- **Multi-threaded** - Non-blocking UI during attack
- **GUI** - Clean PyQt6 interface, no terminal needed

## Supported Formats

- **AuthMe Plugin** (Minecraft) - `SHA256(SHA256(password) + salt)`  **Primary**
- **Generic Salted SHA-256** - Easily adaptable

## How to Use

1. **Prepare Hash & Salt** - Extract from AuthMe database 
2. **Open HashCracker** - Double-click app or run `python HashCracker.py`
3. **Enter Hash & Salt** - Paste values into input fields
4. **Set Length** - Estimate password length (1-12 chars)
5. **Choose Charset** - Select: a-z, A-Z, 0-9, All, Letters, or Alphanumeric
6. **Click START** - Watch progress and wait for result

### Example
```
Input: Hash: e88a87bae4c675b6f137ac88205243edc6fb2c0995a76ecfce996c238611ca12
       Salt: aaed3c56d23ee4f4
       Length: 6
       Charset: a-z

Output: FOUND! Password: leoleo (2,847,256 attempts in 42 seconds)
```

## Performance

6-char lowercase: ~300M combinations = 60-90 seconds | 5-char: 2-3 seconds | 7-char: 45+ minutes

Speed depends on CPU cores, password length, and charset. Use smaller charset and length for faster results.

## How It Works

For each password candidate: `inner_hash = SHA256(password)` → `combined = inner_hash + salt` → `final_hash = SHA256(combined)`. If `final_hash == target`, password is found. Brute-force tests all combinations.

## Limitations

- Only SHA-256 salted hashes (not bcrypt, scrypt, Argon2, etc.)
- Exponential time growth with password length  
- No GPU acceleration (CPU only)
- Requires knowing approximate password length

## Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Hashing**: hashlib.sha256
- **Threading**: Multi-threaded brute-force
- **Build Tool**: PyInstaller (for standalone apps)

## Legal Notice

**LEGAL USE**: Educational purposes, authorized penetration testing with written permission, testing your own systems only.

**ILLEGAL USE**: Unauthorized password cracking, hacking, theft, fraud = **Criminal prosecution, jail time, fines**.

You are responsible for following your local laws.

## License

Educational use only. No warranty provided.