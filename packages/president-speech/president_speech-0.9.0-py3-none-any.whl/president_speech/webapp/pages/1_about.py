import streamlit as st

markdown = '''
# president-speech
- Presidents of the Republic of Korea Speeches
- Parquet, provided in the form of sqlite db file
- Comes with simple cli

### $ pip install president-speech
- https://pypi.org/project/president-speech/


### SUMMARY OF PROVIDED DATA
- data per case can be checked in the following ways
- https://www.pa.go.kr/research/contents/speech/index.jsp?spMode=view&catid=c_pa02062&artid={division_number}
- some data show date values as empty columns or years only
  ![image](https://github.com/edu-data-mario/president-speech/assets/134017660/7efd02c4-0674-483f-bb27-458a04efe3d0)

    | president | size | min(date)  | max(date)  |
    |:----------|:-----|:-----------|:-----------|
    | 이승만       | 998  | 1948.07.24 | 1959.03.10 |
    | 윤보선       | 3    | 1960.08.13 | 1960.09.15 |
    | 박정희       | 1270 | 1963.12.17 | 1979.10.26 |
    | 최규하       | 58   | 1979.10.27 | 1980.08.16 |
    | 전두환       | 602  | 1980.06.05 | 1987.02.16 |
    | 노태우       | 601  | 1988.02.25 | 1992.10.05 |
    | 김영삼       | 728  | 1993.01.09 | 1998.01.23 |
    | 김대중       | 822  | 1998.02.25 | 2003.02.17 |
    | 노무현       | 780  | 2003.02.25 | 2008.01.28 |
    | 이명박       | 1027 | 2008.02.25 | 2013.02.07 |
    | 박근혜       | 493  | 2013.02.24 | 2016.10.26 |
    | 문재인       | 1389 | 2017.05.10 | 2022.03.30 |

    ```python
    >>> df.info()
    
    <class 'pandas.core.frame.DataFrame'>
    Index: 8771 entries, 5368 to 102591
    Data columns (total 7 columns):
     #   Column           Non-Null Count  Dtype 
    ---  ------           --------------  ----- 
     0   division_number  8771 non-null   int64 
     1   president        8771 non-null   object
     2   title            8771 non-null   object
     3   date             8771 non-null   object
     4   location         8771 non-null   object
     5   kind             8771 non-null   object
     6   speech_text      8771 non-null   object
    dtypes: int64(1), object(6)
    memory usage: 548.2+ KB
    ```

### Use
```bash
$ pip install president-speech

$ ps-wordcount -h     
usage: ps-word-count [-h] [-t | -p] word

Word frequency output from previous presidential speeches

positional arguments:
  word         Search word

optional arguments:
  -h, --help   show this help message and exit
  -t, --table  Table Format Output
  -p, --plot   Format Output

$ ps-word-count -p 독립
문재인  [954]  ****************************************
이승만  [430]  ******************
박정희  [361]  ****************
이명박  [176]  ********
김대중  [171]  ********
전두환  [169]  ********
노무현  [167]  *******
노태우  [131]  ******
김영삼  [114]  *****
박근혜  [ 71]  ***
최규하  [  4]  *
윤보선  [  0]
```

```bash
$ ps-word-count -t 독립
|    | president   |   mention |
|---:|:------------|----------:|
|  0 | 문재인      |       954 |
|  1 | 이승만      |       430 |
|  2 | 박정희      |       361 |
|  3 | 이명박      |       176 |
|  4 | 김대중      |       171 |
|  5 | 전두환      |       169 |
|  6 | 노무현      |       167 |
|  7 | 노태우      |       131 |
|  8 | 김영삼      |       114 |
|  9 | 박근혜      |        71 |
| 10 | 최규하      |         4 |
| 11 | 윤보선      |         0 |

```

### Living for TODAY
```
▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▓▒▒▓▒▒▒▒
▒▒▒▒▓▒▒▓▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒
▒▓▒▒▒▒▒▒▒▒▓▒
▒▒▓▓▓▓▓▓▓▓▒▒
▒▒▒▒▒▒▒▒▒▒▒▒
'''

st.markdown(markdown)
