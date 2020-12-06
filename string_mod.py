#! /usr/bin/python

import json
import unicodedata
from sys import stdin
import re
import datetime

input_file_name="./strings.json"
input_file_json: json
input_file_json = None
user_cmd=str()
output_file_name="./strings_out{}.json"

padding_filtered = set()

def input_cmd_parser(input_str):
    cmd = input_str[0]
    if cmd == "h":
        print_help()
    elif cmd == "p":
        hangul_padding_toggle()
    elif cmd == "w":
        if len(padding_filtered) != 0:
            print("공백 필터링 모드입니다. 재삽입합니다.")
            hangul_padding_toggle()
        print("저장하는 중...")
        with open(output_file_name.format(datetime.datetime.now().isoformat()), 'w') as output_file:
            json.dump(input_file_json, output_file)
    elif cmd == "s":
        search()
    elif cmd == "e":
        edit()
    elif cmd == "q":
        exit()
    else:
        raise SyntaxError

def input_decimal_parser(input_str):
    if re.search("[a-zA-Z]", input_str) != None:
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
    if input_str_lst != None:
        return range(start, end)
    return [int(input_str)]

def hangul_padding_toggle():
    if len(padding_filtered) == 0:
        print("공백 필터링 적용 중...")
        for i in range(len(input_file_json)):
            unpadded = hangul_pad_del(input_file_json[i])
            if unpadded == None:
                continue;
            input_file_json[i] = unpadded
            padding_filtered.add(i)
    else:
        print("공백 필터링 해제 중...")
        padded_list = list(padding_filtered)
        padded_list.sort()
        for i in padded_list:
            padded = hangul_pad_add(input_file_json[i])
            input_file_json[i] = padded
            padding_filtered.remove(i)

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

    if has_lo == False:
        return None
    if lo_but_no_sp == True:
        return None

    return no_pad_buf + trail_sp

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

def print_help():
    print("==== 도움말 ====")
    print("* 스트링 출력: 읽고 싶은 번호 혹은 범위를 입력해 주세요")
    print("예시:")
    print("> 80 (단일)")
    print("> 10188 - 10241(시작 - 끝)")
    print("> 10730, 10(시작, 열 갯수)")
    print("공백 필터 여부, 스트링 번호, 스트링 순으로 출력됩니다.")
    print("")
    print("* 다른 명령어:")
    print("p: 한글패치 정렬용 공백 필터링 토글")
    print("s: 검색, e: 수정")
    print("w: 현재까지 수정사항 strings_out[현재일시].json에 저장")
    print("h: 도움말, q: 종료")
    print("")
    print("==== ====== ====")

def print_line(linenum):
    line_content = input_file_json[linenum]
    if len(padding_filtered) == 0:
        print(linenum, line_content)
    else:
        flag = linenum in padding_filtered
        if flag:
            print("[*]", linenum, line_content)
        else:
            print("[ ]", linenum, line_content)

def search():
    print("검색할 문자열을 입력해 주세요")
    print(">> ", end="", flush=True)
    input_str = stdin.readline()
    input_str = input_str[:-1] # assuming \n
    for i in range(len(input_file_json)):
        if input_str in input_file_json[i]:
            print_line(i)

def edit():
    print("수정할 줄 번호를 입력해 주세요")
    print(">> ", end="", flush=True)
    input_str = stdin.readline()
    input_str = input_str[:-1] # assuming \n
    if input_str.isdecimal() != True:
        raise SyntaxError
    linenum = int(input_str)
    print("수정할 문자열을 입력해 주세요")
    print_line(linenum)
    print(">> ", end="", flush=True)
    input_str = stdin.readline()
    input_str = input_str[:-1] # assuming \n
    input_file_json[linenum] = input_str
    print("수정 완료:")
    print_line(linenum)


with open(input_file_name) as input_file:
#    input_file_contents = input_file.read()
    print("strings.json was successfully open")
    input_file_json = json.load(input_file)
    print("json successfully parsed")

print_help()
while 1:
    # start of input
    print("> ", end="", flush=True)
    input_str = stdin.readline()
    # end of input
    try:
        if not input_str[0].isdecimal():
            input_cmd_parser(input_str)
            continue
        read_list = input_decimal_parser(input_str)
    except (SyntaxError, ValueError):
        print("알 수 없는 명령어")
        continue
    except IndexError:
        print("범위 초과")
        continue

    try:
        for i in read_list:
            print_line(i)
    except (IndexError, ValueError):
        print("범위 초과")
        continue

