<center>
	<img src="./readme/images/head_image_1.png" width="100%" alter="석줄요 소개 1" />
	<img src="./readme/images/head_image_2.png" width="100%" alter="석줄요 소개 2" />
	<img src="./readme/images/head_image_3.png" width="100%" alter="석줄요 소개 3" />
</center>
<br/><br/>

# Initialization

## Submodule
<pre>
git submodule update --init --recursive

cd ./server
npm install

cd ../app
npm install
</pre>
<br/>

## Python Enviroment
<pre>
python -m venv .env

# unix & mac 
source .env/bin/activate 

# windows
.env\Scripts\activate.bat

# install packages
pip install -r requirements.txt 
</pre>

# News Recommandation

1. Topic
2. User based collaborative filtering
3. Item based collaborative filtering
4. News with preferred hashtag
5. Contents based filtering 

## 1. Topic

	언론사 RSS 
		🡢 뉴스 수집 
			🡢 뉴스 해시태그 추출 
				🡢 기간 중 가장 많이 모인 해시태그 뉴스 추천

    * 일정 수준 이상으로 모인 해시태그만 선정

## 2. User Based CF

	유저(A)가 선호 해시태그가 비슷한 유저(B)를 선정 
		🡢 유저(B)가 선호하는 뉴스 중 유저(A)가 보지 못한 뉴스 추천 

## 3. Item Based CF

	유저가 선호하는 해시태그를 가지고있는 뉴스 추천

## 4. Contents Based Filtering

	사용자 성별, 나이별 가장 많이보는 뉴스 추천