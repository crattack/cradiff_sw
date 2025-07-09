# cra-diff_share

**radare2를 이용한, diffing tool 플랫폼 만들기 위한 초기 코드**
# 환경
- Ubuntu 20.4 환경
  
# 필수 패키지
- sudo apt install build-essential
- radare2 설치
  - git clone https://github.com/radareorg/radare2
  - radare2/sys/install.sh
- sudo apt install graphviz
- sudo apt install python3-pip
- pip install r2pipe
  - python3 가상화 사용하라고 할 경우 강제 시스템에 설치 : pip install r2pipe --break-system-packages
- r2pm -ic r2ghidra
  - 오류 발생 시 sudo 붙여서 진행
  - r2pm -ic r2ghidra-sleigh
    - apt install unzip pkg-config
- pip3 install r2pipe bs4 graphviz
- dot  설치 : sudo apt-get install graphviz

# 개발 요구 사항
1. r2pipe를 통한 통신 진행
2. diffing 결과에 대한 ASM, pseudo code, CFG(Compare Function Graphic) 기능 추가
3. 보고서에 대한 정리 필요

# 실습 바이너리 파일
- wget https://msdl.microsoft.com/download/symbols/ntkrnlmp.exe/F7E31BA91047000/ntkrnlmp.exe -O ntkrnlmp.exe.x64.10.0.22621.1344
- wget https://msdl.microsoft.com/download/symbols/ntkrnlmp.exe/17B6B7221047000/ntkrnlmp.exe -O ntkrnlmp.exe.x64.10.0.22621.1413
