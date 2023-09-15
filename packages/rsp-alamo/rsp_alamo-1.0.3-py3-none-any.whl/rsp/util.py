# -*- coding: UTF-8 -*-
import re
import warnings
import pkg_resources
from typing import List, Tuple, Optional

from .rsp_tokenizer import RspBertTokenizer

warnings.filterwarnings('ignore')


added_tokens = ['[RS]', '[UUID]', '[DIGIT]', '[IP]', '[MD5]', ' ']


class RspUtil:
    def __init__(self, vocab_file: Optional[str] = None):
        if vocab_file is None:
            vocab_file = pkg_resources.resource_filename(__name__, 'bert-base-multilingual-cased')

        self.tokenizer = RspBertTokenizer.from_pretrained(vocab_file)
        self.tokenizer.add_tokens(added_tokens, special_tokens=True)
        self.uuid_pat = re.compile(r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}')
        self.md5_pat = re.compile(r'(?<![a-fA-F0-9])[a-fA-F0-9]{32}(?![a-fA-F0-9])|'
                                  r'(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])|'
                                  r'(?<![a-fA-F0-9])[a-fA-F0-9]{128}(?![a-fA-F0-9])')
        self.digit_pat = re.compile(r'(?<![a-zA-Z0-9])\d{4,}(?![a-zA-Z0-9])')
        self.ip_pat = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
        self.num_tokens_th = 4
        self.token_len_th = 6

    def sub_uuid(self, text: str) -> str:
        return self.uuid_pat.sub('[UUID]', text)

    def sub_digits(self, text: str) -> str:
        return self.digit_pat.sub('[DIGIT]', text)

    def sub_ip(self, text: str) -> str:
        return self.ip_pat.sub('[IP]', text)

    def sub_md5(self, text: str) -> str:
        return self.md5_pat.sub('[MD5]', text)

    def text2tokens(self, text: str) -> List[str]:
        text = self.sub_uuid(text)
        text = self.sub_md5(text)
        text = self.sub_digits(text)
        text = self.sub_ip(text)
        return self.tokenizer.tokenize(text)

    def locate_rs(self, tokens: List[str]) -> List[Tuple[int, int]]:
        ans = []

        n = len(tokens)
        if n < self.num_tokens_th:
            return ans

        left, right = 0, 1
        while right < n:
            # start token length should be shorter than or equal to 3
            if len(tokens[left]) > 3 or tokens[left].startswith('##'):
                left = right
                right += 1
                continue
            if tokens[right].startswith('##'):
                if len(tokens[right]) <= self.token_len_th:
                    cnt = 0
                    while right < n and tokens[right].startswith('##'):
                        if len(tokens[right]) > self.token_len_th:
                            left = right
                            right += 1
                            break
                        # sum of token with length shorter than 4
                        if len(tokens[right]) <= 4:
                            cnt += 1
                        right += 1

                    if right - left >= self.num_tokens_th:
                        # compute the ratio of tokens with length shorter than token_len_th
                        if cnt / (right - left - 1) >= 0.6:
                            ans.append((left, right))
                        left = right
                        right += 1
                else:
                    while right < n and tokens[right].startswith('##'):
                        right += 1
                    if right < n:
                        left = right
                        right += 1
            else:
                left = right
                right += 1

        return ans

    def replace_rs(self, text: str, repl: str = '[RS]') -> str:
        tokens = self.text2tokens(text)
        indexes = self.locate_rs(tokens)

        # drop random string backwards to avoid influence on smaller indexes
        for item in indexes[::-1]:
            left, right = item[0], item[1]
            tokens = tokens[:left] + [repl] + tokens[right:]

        return_text = ''
        for token in tokens:
            return_text += token if not token.startswith('##') else token[2:]
        return return_text

    def drop_rs(self, text: str) -> str:
        tokens = self.text2tokens(text)
        indexes = self.locate_rs(tokens)

        # drop random string backwards to avoid influence on smaller indexes
        for item in indexes[::-1]:
            left, right = item[0], item[1]
            tokens = tokens[:left] + tokens[right:]

        return_text = ''
        for token in tokens:
            return_text += token if not token.startswith('##') else token[2:]
        return return_text
