#! /usr/bin/python

import json
import unicodedata
from sys import stdin
import sys
import re
import os

WORK_FOLDER="./UTKRStrMod"
INDEX_CACHE_FILE_NAME="str_cache.txt"
JSON_FILE_NAME="strings.json"

INDEX_FILE = None
ASM_FILE = None

def print_help():
    print("==== 도움말 ====")
    print("* 스트링 출력: 읽고 싶은 번호 혹은 범위를 입력해 주세요")
    print("예시:")
    print("> 16858 (단일)")
    print("> 11890 - 11940(시작 - 끝)")
    print("> 1010, 10(시작, 열 갯수)")
    print("공백 필터 여부, 스트링 번호, 스트링 순으로 출력됩니다.")
    print("")
    print("* 다른 명령어:")
    print("p: 한글패치 정렬용 공백 필터링 토글")
    print("s: 검색, i: 인덱스 생성/새로고침")
    print("h: 도움말, q: 종료")
    print("")
    print("==== ====== ====")

def input_cmd_parser(input_str):
    cmd = input_str[0]
    if cmd == "h":
        print_help()
    elif cmd == "p":
        INDEX_FILE.hangul_padding_toggle()
    elif cmd == "s":
        INDEX_FILE.search()
    elif cmd == "i":
        INDEX_FILE.create_index_cache()
        INDEX_FILE.open_index_cache()
    elif cmd == "q":
        sys.exit()
    else:
        raise SyntaxError

def input_decimal_parser(input_str):
    if re.search("[a-zA-Z]", input_str) is not None:
        raise SyntaxError
    input_str_lst = None
    if "-" in input_str:
        input_str_lst = input_str.split("-")
        if len(input_str_lst) != 2:
            raise SyntaxError
        start = int(input_str_lst[0])
        end = int(input_str_lst[1]) + 1
    if "," in input_str:
        input_str_lst = input_str.split(",")
        if len(input_str_lst) != 2:
            raise SyntaxError
        start = int(input_str_lst[0])
        offset = int(input_str_lst[1])
        end = start + offset
    if input_str_lst is not None:
        return range(start, end)
    return [int(input_str)]


class Paddable:
    def __init__(self):
        self.padding_filtered = set()

    def hangul_padding_toggle(self):
        if len(self.padding_filtered) == 0:
            print("공백 필터링 적용 중...")
            for i in range(len(self.file_contents)):
                unpadded = self.hangul_pad_del(self.file_contents[i])
                if unpadded is None:
                    continue
                self.file_contents[i] = unpadded
                self.padding_filtered.add(i)
        else:
            print("공백 필터링 해제 중...")
            padded_list = list(self.padding_filtered)
            padded_list.sort()
            for i in padded_list:
                padded = self.hangul_pad_add(self.file_contents[i])
                self.file_contents[i] = padded
                self.padding_filtered.remove(i)

    @staticmethod
    def hangul_pad_del(input_line):
        # returns None if the line doesn't seem to be padded

        # Let's try preserving all trailing spaces
        rstrip_len = len(input_line.rstrip())
        trail_sp = input_line[rstrip_len:]

        # testing if the string is padded - assuming every "Lo" is hangul
        # 1. A row has to have at least one "Lo"
        # 2. Every "Lo" has to be followed by space
        has_lo = False
        lo_but_no_sp = False
        no_pad_buf = str()

        skip_flag = False

        for j in range(len(input_line)):
            if skip_flag:
                skip_flag = False
                continue
            new_chr = input_line[j]
            no_pad_buf += new_chr

            if unicodedata.category(new_chr) != "Lo":
                continue

            has_lo = True

            if j+1 == len(input_line):
                # lo_but_no_sp = True
                # we have already deleted all trailing space
                break

            next_chr = input_line[j+1]
            if next_chr != " ":
                # & is linebreak, and appears right after "Lo" in padded
                # We have to preserve this, while not messing up paddedness detection
                if next_chr == "&":
                    continue
                lo_but_no_sp = True
                break

            # Current chr is Lo, and next is (padding) space.
            # We don't need to check the next, and also skip adding no_pad_buf
            skip_flag = True

        if not has_lo:
            return None
        if lo_but_no_sp:
            return None

        return no_pad_buf + trail_sp

    @staticmethod
    def hangul_pad_add(input_line):
        # Let's try preserving all trailing spaces
        rstrip_len = len(input_line.rstrip())
        trail_sp = input_line[rstrip_len:]

        padded_buf = str()

        for j in range(len(input_line)):
            new_chr = input_line[j]
            padded_buf += new_chr
            if unicodedata.category(new_chr) != "Lo":
                continue

            if j+1 == len(input_line):
                break

            # No padding before linebreak(&)
            if input_line[j+1] == "&":
                continue

            # Now probably good to pad
            padded_buf += " "

        return padded_buf + trail_sp

class TextView:
    def print_line(self, linenum):
        line_content = self.file_contents[linenum]
        if len(self.padding_filtered) == 0:
            print(linenum, line_content)
        else:
            flag = linenum in self.padding_filtered
            if flag:
                print("[*]", linenum, line_content)
            else:
                print("[ ]", linenum, line_content)

    def search(self):
        print("검색할 문자열을 입력해 주세요")
        print(">> ", end="", flush=True)
        input_str = stdin.readline()
        input_str = input_str[:-1] # assuming \n
        for i in range(len(self.file_contents)):
            if input_str in self.file_contents[i]:
                self.print_line(i)

class StrIndex(Paddable, TextView):
    def __init__(self, path):
        Paddable.__init__(self)
        self.cache_path = path
        self.file_contents = None

        if not self.open_index_cache():
            print("Index cache was not found")
            print("Opening {} instead".format(JSON_FILE_NAME))
            if not os.path.isfile(JSON_FILE_NAME):
                print("FATAL: {} was not found too".format(JSON_FILE_NAME))
                sys.exit(-1)
            with open(JSON_FILE_NAME) as input_file:
                # input_file_contents = input_file.read()
                print("{} was successfully open".format(JSON_FILE_NAME))
                self.file_contents = json.load(input_file)
                print("json successfully parsed")

    def open_index_cache(self):
        if not os.path.isfile(self.cache_path):
            return False
        with open('{}/{}'.format(WORK_FOLDER, INDEX_CACHE_FILE_NAME)) as idx_cache_file:
            idx_cache_list = idx_cache_file.readlines()
        print("Index cache was successfully open")
        self.file_contents = self.DeserializedLines(idx_cache_list)
        print("Deserialization complete")
        return True

    def create_index_cache(self):
        if not os.path.isdir("./code"):
            print("ERROR: code folder was not found")
            return False

        # subprocess is probably better but whatever ¯\_(ツ)_/¯
        if not os.path.isdir(WORK_FOLDER):
            os.mkdir(WORK_FOLDER)
        print("Creating index cache...")
        os.system('grep -r ./code/ -e "push\\.cst string" > {}'
                .format(self.cache_path))
        print("Index cache was created")
        return True

    class DeserializedLines:
        class DeserializedLine:
            def __init__(self, input_line):
                input_line = input_line.strip()
                splt_ln = input_line.split(":")
                self.path = splt_ln[0]
                self.asmaddr = splt_ln[1]

                idx_quot = input_line.find('"')
                self.line = input_line[idx_quot+1:-1]

        def __init__(self, input_lines):
            self.lnlist = []
            for line in input_lines:
                self.lnlist.append(self.DeserializedLine(line))
            self.edited_lines = set()

        def __getitem__(self, key):
            return self.lnlist[key].line

        def __setitem__(self, key, value):
            self.lnlist[key].line = value

        def __len__(self):
            return len(self.lnlist)

def edit():
    print("수정할 줄 번호를 입력해 주세요")
    print(">> ", end="", flush=True)
    input_str = stdin.readline()
    input_str = input_str[:-1] # assuming \n
    if not input_str.isdecimal():
        raise SyntaxError
    linenum = int(input_str)
    print("수정할 문자열을 입력해 주세요")
    print_line(linenum)
    print(">> ", end="", flush=True)
    input_str = stdin.readline()
    input_str = input_str[:-1] # assuming \n
    FILE_CONTENTS[linenum] = input_str
    print("수정 완료:")
    print_line(linenum)

if __name__ == '__main__':
    cache_file_path = WORK_FOLDER + "/" + INDEX_CACHE_FILE_NAME
    INDEX_FILE = StrIndex(cache_file_path)

    print_help()
    while 1:
        # start of input
        print("> ", end="", flush=True)
        main_cmd = stdin.readline()
        # end of input
        try:
            if not main_cmd[0].isdecimal():
                input_cmd_parser(main_cmd)
                continue
            read_list = input_decimal_parser(main_cmd)
        except (SyntaxError, ValueError):
            print("알 수 없는 명령어")
            continue
        except IndexError:
            print("범위 초과")
            continue

        try:
            for main_prn_ln in read_list:
                INDEX_FILE.print_line(main_prn_ln)
        except (IndexError, ValueError):
            print("범위 초과")
            continue
