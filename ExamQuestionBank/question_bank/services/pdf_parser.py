import enum
import re
import io

import pdfplumber
import wordninja


class Flag(enum.Enum):
    BEGIN = -2
    QUESTION = -1
    OPTION_1 = 0
    OPTION_2 = 1
    OPTION_3 = 2
    OPTION_4 = 3


class PDFParser:

    @staticmethod
    def split_en_keep_zh(text: str):
        tokens = re.findall(r'[\u4e00-\u9fff]+|[A-Za-z]+|[0-9]+|[^\w\s]|[\s]+', text)

        result = []
        for tok in tokens:
            # 中文
            if re.match(r'^[\u4e00-\u9fff]+$', tok):
                result.append(tok)
            # 英文
            elif re.match(r'^[A-Za-z]+$', tok):
                result.append(" ".join(wordninja.split(tok)))
            # 其他
            else:
                result.append(tok)

        return "".join(result)

    @staticmethod
    def parse_questions(file):
        questions = []
        level = ""
        category = ""
        subject = ""
        time_length = ""
        
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            temp = {
                "question": "",
                "options": [
                    "",
                    "",
                    "",
                    ""
                ]
            }
            
            flag = Flag.BEGIN

            for index, page in enumerate(pdf.pages):
                for word in page.extract_words():
                    if index == 0:
                        
                        if word["bottom"] < 205: # \ue12b禁止使用電子計算器。 此行以下 (只有在第一頁)                 
                            if level_ := re.fullmatch(r"別：(.*)", word['text']):
                                level = level_.group(1).strip()
                                print("LEVEL", level)
                                continue
                            if category_ := re.fullmatch(r"科：(.*)", word['text']):
                                category = category_.group(1).strip()
                                print("CATEGORY", category)
                                continue
                            if subject_ := re.fullmatch(r"目：(.*)", word['text']):
                                subject = subject_.group(1).strip()
                                print("SUBJECT", subject)
                                continue
                            if time_length_ := re.fullmatch(r"考試時間：(.*)", word['text']):
                                time_length = time_length_.group(1).strip()
                                print("TIME LENGTH", time_length)
                                continue
                            
                            print("SKIP", word['text'])
                            continue
                    else:
                        if re.fullmatch(r"代號：[0-9]+|頁次：[0-9]+－[0-9]+", word['text']): # 移除代號和頁次
                            print("移除代號和頁次:", word['text'])
                            continue
                            
                    if word['x0'] < 55: # 題號位置
                        if flag != Flag.BEGIN:
                            temp["question"] = PDFParser.split_en_keep_zh(temp["question"])
                            for index, option in enumerate(temp["options"]):
                                temp["options"][index] = PDFParser.split_en_keep_zh(option)
                            questions.append(temp)
                            temp = {
                                "question": "",
                                "options": [
                                    "",
                                    "",
                                    "",
                                    ""
                                ]
                            }
                        flag = Flag.QUESTION
                        continue

                    match word["text"][0]:
                        case "\ue18c":
                            flag = Flag.OPTION_1
                        case "\ue18d":
                            flag = Flag.OPTION_2
                        case "\ue18e":
                            flag = Flag.OPTION_3
                        case "\ue18f":
                            flag = Flag.OPTION_4
                        
                    if flag == Flag.QUESTION:
                        print("QUESTION", word["text"])
                        temp["question"] += word["text"]
                    else:
                        print(flag, word["text"])
                        option_content = word["text"].lstrip(u"\ue18c\ue18d\ue18e\ue18f")
                        if option_content:
                            temp["options"][flag.value] += option_content

            temp["question"] = PDFParser.split_en_keep_zh(temp["question"])
            for index, option in enumerate(temp["options"]):
                temp["options"][index] = PDFParser.split_en_keep_zh(option)
            questions.append(temp)
        return {
            "level": level,
            "category": category,
            "subject": subject,
            "time_length": time_length,
            "questions": questions
        }
    
    def parse_answers(file):
        answers = []
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    answers.extend(list(filter(lambda a: a, table[1][1:])))
            notes = "".join(re.findall(r"備 註： .*", page.extract_text()))
        
        return {
            "notes": notes,
            "answers": answers
        }