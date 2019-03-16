#!/bin/sh
IMAGE_DIR=./images_1
URL_PRE="http://db.history.go.kr/servlet/image_proxy.jsp?filePath=/s_img/K_DB/pn/001/pn_001_"
URL_POST=".jpg"
START_PAGE=1
END_PAGE=432

mkdir -p $IMAGE_DIR

echo ">> image download"
for i in $(seq -f "%04g" $START_PAGE $END_PAGE)
do
	url="$URL_PRE$i$URL_POST"
	curl -o $IMAGE_DIR/$i.jpg "$url" > /dev/null 2>&1
	((10#$i % 10 == 0)) && echo "$((10#$i)) ... processed"
done

echo "\n>> file check"
success=true
for i in $(seq -f "%04g" $START_PAGE $END_PAGE)
do
	if [ ! -e "$IMAGE_DIR/$i.jpg" ]; then
		echo "$i.jpg not exist"
		success=false
	fi
done

if [ "$success" == true ]; then
	echo ">> done well"
fi
