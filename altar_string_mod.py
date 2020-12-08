#! /usr/bin/python

import shutil
import readline
import json
import unicodedata
import sys
import re
import os

WORK_FOLDER = "./UTKRStrMod"
INDEX_CACHE_FILE_NAME = "str_cache.txt"
JSON_FILE_NAME = "strings.json"

INDEX_FILE = None
ASM_FILE = None
FILE_REF = None

def print_help():
    print("==== 도움말 ====")
    print("* 스트링 출력: 읽고 싶은 번호 혹은 범위를 입력해 주세요")
    print("예시:")
    print("> 16858 (단일)")
    print("> 11890 - 11940 (시작 - 끝)")
    print("> 1010, 10 (시작, 열 갯수)")
    print("공백 필터 여부, 스트링 번호, 스트링 순으로 출력됩니다.")
    print("")
    print("* 다른 명령어:")
    print("p: 한글패치 정렬용 공백 필터링 토글")
    print("s: 검색, r: 인덱스 생성/새로고침")
    if ASM_FILE is None:
        print("o: 수정 모드 진입")
    else:
        print("c: 수정 모드 종료")
        print("w: 저장, e: 스트링 수정")
    print("h: 도움말, q: 종료")
    print("")
    print("==== ====== ====")

def parse_input_cmd(input_str):
    global ASM_FILE

    cmd_match_fail = 0
    cmd = input_str[0]
    
    # common cmd
    if cmd == "h":
        print_help()
    elif cmd == "p":
        FILE_REF.hangul_padding_toggle()
    elif cmd == "s":
        FILE_REF.search()
    elif cmd == "r":
        INDEX_FILE.create_index_cache()
        INDEX_FILE.open_index_cache()
    else:
        cmd_match_fail += 1

    # index mode cmd
    if ASM_FILE is None:
        if cmd == "q":
            sys.exit()
        elif cmd == "o":
            ASM_FILE = INDEX_FILE.open_asm_file()
        else:
            cmd_match_fail += 1

    # asm mode cmd
    else:
        if cmd == "c":
            print("현재 열려 있는 {} 파일을 종료합니다...".format(ASM_FILE.asm_path))
            ASM_FILE = None
        elif cmd == "e":
            ASM_FILE.edit()
        elif cmd == "w":
            ASM_FILE.write()
        else:
            cmd_match_fail += 1

    if cmd_match_fail == 2:
        # There was no action match
        raise SyntaxError

def parse_input_decimal(input_str):
    if re.search("[a-zA-Z]", input_str):
        raise SyntaxError
    input_str_lst = None
    if "-" in input_str:
        input_str_lst = input_str.split("-")
        if len(input_str_lst) != 2:
            raise SyntaxError
        start = int(input_str_lst[0])
        end = int(input_str_lst[1]) + 1
        return range(start, end)
    if "," in input_str:
        input_str_lst = input_str.split(",")
        if len(input_str_lst) != 2:
            raise SyntaxError
        start = int(input_str_lst[0])
        offset = int(input_str_lst[1])
        end = start + offset
        return range(start, end)

    return [int(input_str)]


class TextListCommon:
    def __init__(self):
        self.text_list_contents: self.DeserializedLines
        self.text_list_contents = None
        self.padding_filtered = set()

    def hangul_padding_toggle(self):
        if len(self.padding_filtered) == 0:
            print("공백 필터링 적용 중...")
            for ln_pair in enumerate(self.text_list_contents):
                unpadded = self.hangul_pad_del(ln_pair[1])
                if unpadded is None:
                    continue
                self.text_list_contents[ln_pair[0]] = unpadded
                self.padding_filtered.add(ln_pair[0])
        else:
            print("공백 필터링 해제 중...")
            padded_list = sorted(self.padding_filtered)
            for i in padded_list:
                padded = self.hangul_pad_add(self.text_list_contents[i])
                self.text_list_contents[i] = padded
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
        no_pad_str_lst = []

        skip_flag = False

        for char_pair in enumerate(input_line):
            if skip_flag:
                skip_flag = False
                continue

            char_cnt = char_pair[0]
            new_chr = char_pair[1]
            no_pad_str_lst.append(new_chr)

            if unicodedata.category(new_chr) != "Lo":
                continue

            has_lo = True

            if char_cnt+1 == len(input_line):
                # lo_but_no_sp = True
                # we have already deleted all trailing space
                break

            next_chr = input_line[char_cnt+1]
            if next_chr != " ":
                # & is linebreak, and appears right after "Lo" in padded
                # We have to preserve this, while not messing up paddedness detection
                if next_chr == "&":
                    continue
                lo_but_no_sp = True
                break

            # Current chr is Lo, and next is (padding) space.
            # We don't need to check the next, and also skip adding no_pad_str_lst
            skip_flag = True

        if not has_lo or lo_but_no_sp:
            return None

        no_pad_str_lst.append(trail_sp)
        return str.join("", no_pad_str_lst)

    @staticmethod
    def hangul_pad_add(input_line):
        # Let's try preserving all trailing spaces
        rstrip_len = len(input_line.rstrip())
        trail_sp = input_line[rstrip_len:]

        padded_str_list = []

        for ln_pair in enumerate(input_line):
            new_chr = ln_pair[1]
            padded_str_list.append(new_chr)
            if unicodedata.category(new_chr) != "Lo":
                continue

            if ln_pair[0]+1 == len(input_line):
                break

            # No padding before linebreak(&)
            if input_line[ln_pair[0]+1] == "&":
                continue

            # Now probably good to pad
            padded_str_list.append(" ")

        padded_str_list.append(trail_sp)
        return str.join("", padded_str_list)

    def print_line(self, linenum):
        line_content = self.text_list_contents[linenum]
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
        input_str = input(">> ")
        for i in range(len(self.text_list_contents)):
            if input_str in self.text_list_contents[i]:
                self.print_line(i)

    class DeserializedLines:
        def __init__(self, input_lines, deserialization):
            self.lnlist = []
            for line in input_lines:
                self.lnlist.append(deserialization(line))

        def __getitem__(self, key):
            return self.lnlist[key]["line"]

        def __setitem__(self, key, value):
            self.lnlist[key]["line"] = value

        def __len__(self):
            return len(self.lnlist)

class StrIndex(TextListCommon):
    def __init__(self, path):
        super().__init__()
        self.cache_path = path

        if not self.open_index_cache():
            print("Index cache was not found")
            print("Opening {} instead".format(JSON_FILE_NAME))
            if not os.path.isfile(JSON_FILE_NAME):
                print("FATAL: {} was not found too".format(JSON_FILE_NAME))
                sys.exit(1)
            with open(JSON_FILE_NAME) as input_file:
                # input_file_contents = input_file.read()
                print("{} was successfully opened".format(JSON_FILE_NAME))
                self.text_list_contents = json.load(input_file)
                print("json successfully parsed")

    def open_index_cache(self):
        if not os.path.isfile(self.cache_path):
            return False
        with open(os.path.join(WORK_FOLDER, INDEX_CACHE_FILE_NAME)) as idx_cache_file:
            idx_cache_list = idx_cache_file.readlines()
        print("Index cache was successfully opened")
        self.text_list_contents = self.DeserializedLines(idx_cache_list, self.deserialization)
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

    def open_asm_file(self):
        # TODO: Error handling when current index file is json
        print("수정할 줄 번호를 입력하세요")
        input_str = input(">> ")
        if not input_str.isdecimal():
            raise SyntaxError
        linenum = int(input_str)
        self.print_line(linenum)
        path = self.text_list_contents.lnlist[linenum]["path"]
        print("위 줄이 포함된 {} 파일을 수정합니다...".format(path))
        return StrAsm(path)

    @staticmethod
    def deserialization(input_line):
        rtn_dict = {}
        input_line = input_line.strip()
        splt_ln = input_line.split(":")
        rtn_dict["path"] = splt_ln[0]
        rtn_dict["asmaddr"] = splt_ln[1]

        idx_quot = input_line.find('"')
        rtn_dict["line"] = input_line[idx_quot+1:-1]
        return rtn_dict

class StrAsm(TextListCommon):
    def __init__(self, path):
        super().__init__()
        self.asm_path = path
        self.string_line_num_list = list()

        lines_to_serialize = list()
        with open(self.asm_path) as f:
            self.asm_code_lines = f.readlines()
        print("asm source was successfully opened")
        for i in range(len(self.asm_code_lines)):
            if not "push.cst string" in self.asm_code_lines[i]:
                continue

            self.string_line_num_list.append(i)
            lines_to_serialize.append(self.asm_code_lines[i])

        self.text_list_contents = self.DeserializedLines(lines_to_serialize, self.deserialization)
        print("Deserialization complete")

    def edit(self):
        print("수정할 줄 번호를 입력해 주세요")
        input_str = input(">> ")
        if not input_str.isdecimal():
            raise SyntaxError
        linenum = int(input_str)
        print("수정할 문자열을 입력해 주세요")
        self.print_line(linenum)
        input_str = input(">> ")
        self.text_list_contents[linenum] = input_str
        print("수정 완료:")
        self.print_line(linenum)

    def write(self):
        backup_path = self.asm_path + ".bak"
        if os.path.isfile(backup_path):
            suffix = 0
            backup_path = backup_path + ".{}"
            while os.path.isfile(backup_path.format(suffix)):
                suffix += 1
            backup_path = backup_path.format(suffix)

        print("Creating a backup as {}...".format(backup_path))
        shutil.copyfile(self.asm_path, backup_path)

        print("현재 열려 있는 {} 파일을 저장합니다...".format(self.asm_path))
        if len(self.padding_filtered):
            print("정렬 공백 필터 상태입니다. 해제합니다...")
            self.hangul_padding_toggle()

        print("Serializing...")
        for line_pair in enumerate(self.string_line_num_list):
            src = self.text_list_contents.lnlist[line_pair[0]]
            # dst = self.asm_code_lines[line_pair[1]]

            serialized_line = '{}: push.cst string "{}"\n'.format(src["asmaddr"], src["line"])
            self.asm_code_lines[line_pair[1]] = serialized_line
            
        print("Writing to disk...")
        with open(self.asm_path, "w") as write_file:
            write_file.writelines(self.asm_code_lines)

        print("저장 완료.")
        print("인덱스 캐시는 자동 갱신되지 않습니다. 직접 새로고침 해 주세요.")

    @staticmethod
    def deserialization(input_line):
        rtn_dict = {}
        input_line = input_line.strip()
        splt_ln = input_line.split(":")
        rtn_dict["asmaddr"] = splt_ln[0]

        idx_quot = input_line.find('"')
        rtn_dict["line"] = input_line[idx_quot+1:-1]
        return rtn_dict

if __name__ == '__main__':
    cache_file_path = os.path.join(WORK_FOLDER, INDEX_CACHE_FILE_NAME)
    INDEX_FILE = StrIndex(cache_file_path)

    print_help()
    while 1:
        FILE_REF = ASM_FILE \
                if ASM_FILE is not None \
                else INDEX_FILE

        main_cmd = input("> ")
        try:
            if not main_cmd[0].isdecimal():
                parse_input_cmd(main_cmd)
                continue

            read_list = parse_input_decimal(main_cmd)

            for main_prn_ln in read_list:
                FILE_REF.print_line(main_prn_ln)
        except SyntaxError:
            print("알 수 없는 명령어")
        except ValueError:
            print("올바르지 않은 값")
        except IndexError:
            print("범위 초과")
