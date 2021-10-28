# Topic1
주제1: 렌즈 조립체 성능 시험 및 정량화 시스템 개발

예상 결과물: 캠을 이용한 실시간 히스토그램 & 엣지검출 SW개발
> 웹캠 또는 usb 캠 사용

## 결과물 실행
> Releases 확인하기  

**현재 EdgeDetector v2.0이 릴리즈 되었습니다. (2021-10-21)**
- 4칸형으로 레이아웃으로 변경
- 블러 타입 선택, 파라미터 값 조정 기능 추가
  > 블러 타입: Gaussian, Median, Bilateral
- 에지 검출기 타입 선택, 파라미터 값 조정 기능 추가
  > Canny, Laplician, Sobel Prewitt
- 스크린샷 기능 추가

![image](https://user-images.githubusercontent.com/30483337/138281931-fbcc2e8f-de3a-4f4b-b34e-0f0c973c236a.png)


현재 EdgeDetector v1.0이 릴리즈 되었습니다. (2021-10-12)
- Gaussian 블러링, CannyEdge로 에지 검출
- CanyEdge의 이력 문턱치 조정 기능

![image](https://user-images.githubusercontent.com/30483337/137175447-8f42382c-b7d9-4a4b-a76e-48018e4cbcfb.png)

## 소스 코드 실행
방법1. git으로 다운받기
```
git clone https://github.com/2021-Capstone-Team1/Topic1.git
cd Topic1
python3 gui.py
```

방법2. `Download Zip`으로 다운받기  

![image](https://user-images.githubusercontent.com/30483337/136502720-538ab817-b743-4649-837d-3c0e71813f0a.png)

```
1. 다운받은 경로에서 압축을 푼다.
2. Window키 + R로 실행검색에서 cmd 입력하여 cmd 창 띄운다.
3. 다운받은 경로로 이동
4. python3 gui.py 로 파일 실행
```
## 엣지 검출 알고리즘
> 리드: 임채룡

## OpenCV를 이용한 캠 연동
> 리드: 송민주

## SW GUI 개발
> 리드: 김하늬

>개발 환경: Windows10, PyCharm, tkinter


