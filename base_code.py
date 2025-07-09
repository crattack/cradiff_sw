import sys
import os
import json
from graphviz import Source
import argparse
import subprocess
import difflib
import r2pipe

def generate_html_diff(code1, code2):
    # 두 코드를 비교
    d = difflib.Differ()
    diff = list(d.compare(code1.splitlines(), code2.splitlines()))

    # HTML 시작
    html_output = """
<html>
<head>
    <title>Code Difference Analysis</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; }
        .normal { color: black; }
        .added { background-color: lightgreen; }
        .removed { background-color: salmon; }
        .changed { background-color: lightblue; }
    </style>
</head>
<body>
    <h2>Code Comparison</h2>
    <pre>
    """

    # diff 결과를 파싱하여 HTML에 추가
    for line in diff:
        class_name = 'normal'
        if line.startswith('+ '):
            class_name = 'added'
        elif line.startswith('- '):
            class_name = 'removed'
        elif line.startswith('? '):
            class_name = 'changed'

        # HTML에 라인 추가
        html_output += f'<div class="{class_name}">{line}</div>'

    # HTML 마무리
    html_output += """
    </pre>
</body>
</html>
    """
    return html_output

def make_pseudo_code(binary_path, function_name):
    try:
        # Radare2 인스턴스 생성 및 바이너리 파일 열기
        r2 = r2pipe.open(binary_path)
        # 초기 분석 수행
        r2.cmd('aaa')
        # 함수의 디컴파일
        code = r2.cmd(f'pdc @ {function_name}')
        r2.quit()  # 자원 정리
        if code:

            return {'content': code}  # 'content' 키에 코드 저장
        else:
            return {'error': "No output from Radare2"}
    except Exception as e:
        return {'error': str(e)}


def cfg_diffing(file1, file2, func_name):
    """두 바이너리 파일의 차이를 radiff2를 사용하여 분석하고 JSON 형식으로 반환합니다."""
    try:
        # radiff2를 사용하여 두 바이너리 파일을 비교
        diff_command = ['radiff2', '-AC', '-g', func_name, '-md', file1, file2]
        result = subprocess.run(diff_command, capture_output=True, text=True)
        # 결과 출력
        if result.stdout:
            return result.stdout
        else:
            return {"error": "No output from radiff2 or error occurred"}
    except Exception as e:
        return {"error": str(e)}

def dot_to_jpg(dot_source, address):
    # Create a Graphviz source from the DOT code
    # engine 테스트 결과
    # sfdp : 분기선이 겹쳐서 가독성 떨어짐
    # fdp : 가독성도 좋고 큰 함수도 잘 그려줌
    # neato, twopi : 가운데로 모여서 분석 불가
    # twopi : 가운데로 모여서 분석 불가
    # circo : 에러 사용 불가
    src = Source(dot_source, engine='fdp')

    try:
        src.render('./result/'+address, format='jpg', cleanup=True)  # This saves the file as 'output_path.jpg'
        print("Graph rendered successfully.")
        return './result/'+address+".jpg"
    except Exception as e:
        print("Failed to render graph:")
        print(str(e))


def extract_data_and_generate_html(file1, file2, data):
    # HTML 헤더 설정
    html_output = """
<html>
<head>
    <title>Function Analysis</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
            overflow: hidden; /* 내용이 넘치면 숨김 */
            text-overflow: ellipsis; /* 내용이 넘칠 경우 말줄임표로 표시 */
            white-space: nowrap;  /* 내용을 한 줄로 표시 */
        }
        th {
            background-color: #f2f2f2;
        }
        .funcname-width {
            width: 200px;  /* 너비를 100px로 설정*/
        }
        .size-width {
            width: 50px
        }
        .address-width {
            width: 100px
        }
        .matchstatus-width {
            width: 100px
        }
        .matchscore-width {
            width: 100px
        }
        .sizediscrepancy-width {
            width: 200px
        }
    </style>
</head>
<body>
    <h2>Function Match Details</h2>
    <table>
        <tr>
            <th class="function-name">Function Name</th>
            <th class="size-width" align=center>Size</th>
            <th class="address-width">Address</th>
            <th class="matchstatus-width">Match Status</th>
            <th class="matchscore-width">Match Score</th>
            <th class="sizediscrepancy-width">Size Discrepancy</th>
        </tr>
    """

    # 데이터 파싱
    #lines = data.strip().split('\n')
    for line in data:
        parts = line.split('|')
        if len(parts) >= 2:
            # 부분 파싱
            func_details = parts[0].strip().split()
            func_name = func_details[0]
            size = int(func_details[1])
            address = func_details[2]

            match_details = parts[1].strip().split()
            match_status = match_details[0]
            match_score = match_details[1].strip('()') if len(match_details) > 1 else 'N/A'

            # second file size
            if match_status == "NEW":
                size_cap = size
            else:
                second_size_details = parts[2].strip().split()
                second_size = int(second_size_details[1])

                # 크기 차이 계산 (예시에서는 같으므로 0으로 표시)
                size_cap = size - second_size  # 이 예제에서는 모든 크기가 같음을 가정

            # HTML 행 추가
            if size_cap != 0:
                # 두 바이너리 파일 비교
                cfg_result = cfg_diffing(file1, file2, address)
                # dot 포멧을 jpg 포멧으로 변경
                a_graphy_tag = dot_to_jpg(cfg_result, address)
                # pseudo code make
                # 두 바이너리 파일의 pseudo 코드 가져오기
                file1_pseudo = make_pseudo_code(file1, func_name)
                file2_pseudo = make_pseudo_code(file2, func_name)

                # 에러 체크
                if 'error' not in file1_pseudo or 'error' not in file2_pseudo:
                    # HTML 생성 및 저장
                    if 'content' not in file2_pseudo:
                        file2_pseudo['content'] = ''
                    html_content = generate_html_diff(file2_pseudo['content'], file1_pseudo['content'])
                else:
                    html_content = "Error generating pseudo code: " + file1_pseudo.get('error', '') + " " + file2_pseudo.get('error', '')

                with open("./result/"+address+".html", "w") as file:
                    file.write(html_content)

                html_output += f"""
                    <tr>
                        <td><a href={a_graphy_tag}>{func_name}</a></td>
                        <td>{size}</td>
                        <td><a href={"./result/"+address+".html"}>{address}</td>
                        <td>{match_status}</td>
                        <td>{match_score}</td>
                        <td>{size_cap}</td>
                    </tr>
                """
                # HTML 출력 (브라우저에서 볼 수 있도록 HTML 파일로 저장하거나, 필요에 따라 다르게 사용)
                with open('result_report.html', 'a+') as file:
                    file.write(html_output)
                    html_output = ''
        # HTML 마무리
    html_output = """
    </table>
</body>
</html>
    """
        # HTML 출력 (브라우저에서 볼 수 있도록 HTML 파일로 저장하거나, 필요에 따라 다르게 사용)
    with open('result_report.html', 'a+') as file:
        file.write(html_output)




def diff_binaries(file1, file2):
    try:
        # radiff2를 사용하여 두 바이너리 파일을 비교
        diff_command = ['radiff2', '-AC', file1, file2]
        result = subprocess.run(diff_command, capture_output=True, text=True)
        # 결과 출력
        if result.stdout:
            lines = result.stdout.split('\n')
            unmatch_lines = [line for line in lines if 'UNMATCH' in line or 'NEW' in line]
            #unmatch_lines = [line for line in lines if re.search(r'\bUNMATCH\b|\bNEW\b', line)]
            return unmatch_lines
        else:
            return {"error": "No output from radiff2 or error occurred"}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Compare two binary files using radiff2.")
    parser.add_argument("file1", help="The path to the first binary file")
    parser.add_argument("file2", help="The path to the second binary file")

    args = parser.parse_args()

    # 두 바이너리 파일 비교
    differences = diff_binaries(args.file1, args.file2)

    # 데이터를 HTML로 파싱
    extract_data_and_generate_html(args.file1, args.file2, differences)

if __name__ == "__main__":
    main()
