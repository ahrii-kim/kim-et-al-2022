from konlpy.tag import Okt, Hannanum, Komoran, Kkma
import MeCab

TOKENIZER = MeCab.Tagger(f"--dicdir /usr/local/lib/mecab/dic/mecab-ko-dic")



def mecab(text: str, space_symbol: str = "▃"):  
    text = text.strip()
    text_ptr = 0
    tokenized = []
    for mor in TOKENIZER.parse(text).split("\n"):
        if "\t" in mor:
            splitted = mor.split("\t")
            token = splitted[0]
            # pos = splitted[1].split(",", 1)[0]

            if text[text_ptr] == " ":
                while text[text_ptr] == " ":
                    text_ptr += 1
                assert text[text_ptr] == token[0]
                if space_symbol:
                    tokenized.append(space_symbol)

            tokenized.append(token)
            text_ptr += len(token)
    return tokenized
