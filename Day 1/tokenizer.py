class CustomTokenizer:
    def __init__(self):
        # Define vocab
        self.char_to_index = {}
        self.index_to_char = {}

        # 1-26: a-z
        for i, c in enumerate("abcdefghijklmnopqrstuvwxyz", start=1):
            self.char_to_index[c] = i
            self.index_to_char[i] = c

        # 27-52: A-Z
        for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", start=27):
            self.char_to_index[c] = i
            self.index_to_char[i] = c

        # 53+: Special characters
        special_chars = "!@#$%^&*()_-+=[]{}|;:',.<>?/~`\"\\ \n\t"
        for i, c in enumerate(special_chars, start=53):
            self.char_to_index[c] = i
            self.index_to_char[i] = c

    def tokenize(self, text):
        """Convert text into list of token ids."""
        token_ids = []
        for char in text:
            if char in self.char_to_index:
                token_ids.append(self.char_to_index[char])
            else:
                print(f"Warning: Unknown character '{char}' – ignored.")
        return token_ids

    def detokenize(self, token_ids):
        """Convert list of token ids back into text."""
        chars = []
        for tid in token_ids:
            if tid in self.index_to_char:
                chars.append(self.index_to_char[tid])
            else:
                print(f"Warning: Unknown token id '{tid}' – ignored.")
        return ''.join(chars)



tokenizer = CustomTokenizer()

text = "Hello, World!"
tokens = tokenizer.tokenize(text)
print("Tokenized:", tokens)

original_text = tokenizer.detokenize(tokens)
print("Detokenized:", original_text)
