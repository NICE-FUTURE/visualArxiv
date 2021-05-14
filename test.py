# -*- "coding: utf-8" -*-

import email
import os
from datetime import datetime
from collections import Counter
import re


eml_dir = "./eml/"
txt_dir = "./txt/"
word_count_dir = "./word_count/"

def eml2txt():
    for filename in os.listdir(eml_dir):
        with open(os.path.join(eml_dir, filename), "r", encoding="utf-8") as fin:
            msg = email.message_from_file(fin)
            date_str = msg["Date"].split(", ")[1].split(" -")[0]
            date = datetime.strptime(date_str, "%d %b %Y %H:%M:%S")
            date_str = date.strftime("%Y-%m-%d_%H-%M-%S")
            with open(os.path.join(txt_dir, "{}.txt".format(date_str)), "w", encoding="utf-8") as fout:
                for par in msg.walk():
                    if not par.is_multipart():
                        lines = par.get_payload(decode=True).decode().split("\n")[12:]
                        cnt = 0
                        mode = None
                        for line in lines:
                            if line.startswith("Title:"):
                                mode = "save"
                                fout.write(line[7:]+"\n")
                            elif line.startswith("Authors:"):
                                mode = "skip"
                            elif line.startswith(r"\\"):
                                if cnt == 0:
                                    cnt += 1
                                    mode = "skip"
                                elif cnt == 1:
                                    cnt += 1
                                    mode = "save"
                                elif cnt == 2:
                                    cnt += 1
                                    mode = "next"
                                elif cnt == 3:
                                    fout.write("\n")
                                    cnt = 1
                                    mode = "skip"
                            elif mode == "save":
                                fout.write(line+"\n")


def word_count():
    with open("./stopwords.txt", "r", encoding="utf-8") as f:
        stopwords = set(f.read().strip().split("\n"))
    for filename in os.listdir(txt_dir):
        in_path = os.path.join(txt_dir, filename)
        out_path = os.path.join(word_count_dir, filename)
        with open(in_path, "r", encoding="utf-8") as fin:
            with open(out_path, "w", encoding="utf-8") as fout:
                content = ["".join(re.findall(r"[a-zA-Z ']", word)) for word in fin.read().replace("\n"," ").replace("\r"," ").replace("\t", " ").split(" ")]
                content = [word for word in content if word.lower() != "" and word.lower() not in stopwords]
                word_count = Counter(content).most_common(20)
                for item in word_count:
                    fout.write("{}:{}\n".format(item[0],item[1]))


def wc2js():
    data = [["count", "null1", "null2", "word", "date"],]
    for filename in os.listdir(word_count_dir):
        path = os.path.join(word_count_dir, filename)
        date = filename.split("_")[0]
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                eles = line.strip().split(":")
                name = eles[0]
                count = int(eles[1])
                data.append([count,0,0,name,date])
    with open("./data.js", "w", encoding="utf-8") as f:
        f.write("var data = {}".format(data))


if __name__ == "__main__":
    wc2js()
