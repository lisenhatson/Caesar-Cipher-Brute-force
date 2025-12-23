import string
from collections import Counter

uppercase = string.ascii_uppercase
lowercase = string.ascii_lowercase

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def encrypt(plaintext, key):
    result = ""
    for char in plaintext:
        if char in uppercase:
            idx = (uppercase.index(char) + key) % 26
            result += uppercase[idx]
        elif char in lowercase:
            idx = (lowercase.index(char) + key) % 26
            result += lowercase[idx]
        else:
            result += char
    return result

def decrypt(ciphertext, key):
    result = ""
    for char in ciphertext:
        if char in uppercase:
            idx = (uppercase.index(char) - key) % 26
            result += uppercase[idx]
        elif char in lowercase:
            idx = (lowercase.index(char) - key) % 26
            result += lowercase[idx]
        else:
            result += char
    return result

def chi_squared_score(text):
    english_freq = {
        'a': 8.167, 'b': 1.492, 'c': 2.782, 'd': 4.253, 'e': 12.702,
        'f': 2.228, 'g': 2.015, 'h': 6.094, 'i': 6.966, 'j': 0.153,
        'k': 0.772, 'l': 4.025, 'm': 2.406, 'n': 6.749, 'o': 7.507,
        'p': 1.929, 'q': 0.095, 'r': 5.987, 's': 6.327, 't': 9.056,
        'u': 2.758, 'v': 0.978, 'w': 2.360, 'x': 0.150, 'y': 1.974,
        'z': 0.074
    }

    text_lower = text.lower()
    letter_count = Counter(c for c in text_lower if c.isalpha())
    total = sum(letter_count.values())

    if total == 0:
        return float('inf')

    chi2 = 0
    for letter in english_freq:
        expected = total * (english_freq[letter] / 100)
        observed = letter_count.get(letter, 0)
        if expected > 0:
            chi2 += ((observed - expected) ** 2) / expected

    return chi2

def index_of_coincidence(text):
    text_clean = ''.join(c for c in text.lower() if c.isalpha())
    n = len(text_clean)

    if n <= 1:
        return 0

    freq = Counter(text_clean)
    ioc = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

    return -abs(ioc - 0.067)

def word_pattern_score(text):
    words = text.lower().split()

    if not words:
        return 0

    score = 0

    avg_length = sum(len(w) for w in words) / len(words)
    length_score = -abs(avg_length - 4.5)
    score += length_score * 10

    text_alpha = ''.join(c for c in text.lower() if c.isalpha())
    if text_alpha:
        vowels = sum(1 for c in text_alpha if c in 'aeiouy')
        vowel_ratio = vowels / len(text_alpha)
        vowel_score = -abs(vowel_ratio - 0.4)
        score += vowel_score * 100

    common_bigrams = {
        'th', 'he', 'in', 'er', 'an', 're', 'on', 'at', 'en', 'nd',
        'ti', 'es', 'or', 'te', 'of', 'ed', 'is', 'it', 'al', 'ar',
        'st', 'to', 'nt', 've', 'ng', 'ha'
    }

    bigram_count = 0
    for i in range(len(text_alpha) - 1):
        if text_alpha[i:i+2] in common_bigrams:
            bigram_count += 1

    if len(text_alpha) > 1:
        bigram_score = bigram_count / (len(text_alpha) - 1)
        score += bigram_score * 50

    common_trigrams = {
        'the', 'and', 'ing', 'ion', 'tio', 'ent', 'ati', 'for', 'her', 'ter'
    }

    trigram_count = 0
    for i in range(len(text_alpha) - 2):
        if text_alpha[i:i+3] in common_trigrams:
            trigram_count += 1

    if len(text_alpha) > 2:
        trigram_score = trigram_count / (len(text_alpha) - 2)
        score += trigram_score * 75

    return score

def fitness_score(text):
    chi2 = chi_squared_score(text)
    chi2_score = -chi2 if chi2 != float('inf') else -1000

    ioc_score = index_of_coincidence(text) * 1000

    pattern = word_pattern_score(text)

    total = chi2_score * 0.4 + ioc_score * 0.3 + pattern * 0.3

    return total

def truncate_text(text, max_len):
    if len(text) <= max_len:
        return text
    return text[:max_len-5] + " (...)"

def bruteforce_basic(ciphertext):
    for key in range(27):
        result = decrypt(ciphertext, key)
        print(f"Key {key}: {result}")

def bruteforce_smart(ciphertext):
    results = []

    for key in range(27):
        result = decrypt(ciphertext, key)
        score = fitness_score(result)

        results.append({
            'key': key,
            'text': result,
            'score': score,
            'chi2': chi_squared_score(result),
            'ioc': index_of_coincidence(result)
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    print(f"\n{Colors.BOLD}Statistical Analysis Results{Colors.END}\n")

    col_widths = [6, 5, 10, 10, 10, 55]

    print("┌" + "┬".join("─" * w for w in col_widths) + "┐")

    header_parts = [
        f"{'Rank':^{col_widths[0]}}",
        f"{'Key':^{col_widths[1]}}",
        f"{'Score':^{col_widths[2]}}",
        f"{'Chi²':^{col_widths[3]}}",
        f"{'IoC':^{col_widths[4]}}",
        f"{'Plaintext':^{col_widths[5]}}"
    ]
    print(f"{Colors.CYAN}{Colors.BOLD}│" + "│".join(header_parts) + f"│{Colors.END}")

    print("├" + "┼".join("─" * w for w in col_widths) + "┤")

    for rank, item in enumerate(results[:10], 1):
        if rank == 1:
            color = Colors.GREEN + Colors.BOLD
            marker = "★★★"
        elif rank == 2:
            color = Colors.YELLOW
            marker = "★★ "
        elif rank == 3:
            color = Colors.BLUE
            marker = "★  "
        else:
            color = ""
            marker = "   "

        rank_str = f"{marker}{rank}"
        truncated_text = truncate_text(item['text'], col_widths[5] - 2)

        row_parts = [
            f"{rank_str:^{col_widths[0]}}",
            f"{item['key']:^{col_widths[1]}}",
            f"{item['score']:^{col_widths[2]}.1f}",
            f"{item['chi2']:^{col_widths[3]}.1f}",
            f"{item['ioc']*1000:^{col_widths[4]}.2f}",
            f"{truncated_text:<{col_widths[5]}}"
        ]
        print(f"│{color}" + f"{Colors.END}│{color}".join(row_parts) + f"{Colors.END}│")

    print("└" + "┴".join("─" * w for w in col_widths) + "┘")

    if len(results) > 10:
        print(f"\n{Colors.BOLD}+ {len(results) - 10} more results with lower scores{Colors.END}")

    best = results[0]
    print(f"\n{Colors.GREEN}{Colors.BOLD}Best Candidate{Colors.END}\n")
    print(f"{Colors.BOLD}Key:{Colors.END} {best['key']}")
    print(f"{Colors.BOLD}Text:{Colors.END} {best['text']}")
    print(f"\n{Colors.BOLD}Metrics:{Colors.END}")
    print(f"  Fitness Score: {best['score']:.2f}")
    print(f"  Chi Squared: {best['chi2']:.2f}")
    print(f"  IoC: {best['ioc']:.4f} (English ~ 0.067)")

def menu():
    while True:
        print(f"\n{Colors.BOLD}Caesar Cipher Tool{Colors.END}")
        print(f"┌{'─' * 30}┐")
        print(f"│ {Colors.CYAN}1{Colors.END} Bruteforce (statistical){' ' * 3}│")
        print(f"│ {Colors.CYAN}2{Colors.END} Bruteforce (basic){' ' * 9}│")
        print(f"│ {Colors.CYAN}3{Colors.END} Encrypt{' ' * 20}│")
        print(f"│ {Colors.CYAN}4{Colors.END} Decrypt with known key{' ' * 5}│")
        print(f"│ {Colors.RED}5{Colors.END} Exit{' ' * 23}│")
        print(f"└{'─' * 30}┘")

        try:
            choice = int(input(f"\n{Colors.BOLD}Select option:{Colors.END} "))

            if choice == 5:
                print(f"{Colors.GREEN}Goodbye{Colors.END}")
                break
            elif choice == 1:
                ciphertext = input("Enter ciphertext: ")
                bruteforce_smart(ciphertext)
            elif choice == 2:
                ciphertext = input("Enter ciphertext: ")
                bruteforce_basic(ciphertext)
            elif choice == 3:
                plaintext = input("Enter plaintext: ")
                key = int(input("Enter key (number): "))
                result = encrypt(plaintext, key)
                print(f"{Colors.GREEN}Encrypted:{Colors.END} {result}")
            elif choice == 4:
                ciphertext = input("Enter ciphertext: ")
                key = int(input("Enter key (number): "))
                result = decrypt(ciphertext, key)
                print(f"{Colors.GREEN}Decrypted:{Colors.END} {result}")
            else:
                print(f"{Colors.RED}Invalid option{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Interrupted{Colors.END}")
            break

if __name__ == "__main__":
    menu()
